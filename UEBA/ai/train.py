import torch
import torch.nn as nn
from tqdm import tqdm
from models.autoencoder import AE
from models.dbscan import train_dbscan, save_dbscan_model
from models.isolation_forest import save_iforest_model, train_iforest
from sklearn.preprocessing import StandardScaler
import sys
import os
import logging
from dotenv import load_dotenv
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from influxdb.influx_reader import get_software_metrics, get_hardware_metrics
import json
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="ueba.log",
)

def create_sequences(data, seq_len):
    sequences = []
    for i in range(len(data) - seq_len):
        seq = data[i:i+seq_len]
        sequences.append(seq)
    return torch.stack(sequences)


def train_autoencoder(df, save_path, epochs=1000, lr=0.001):
    try:
        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(df[["cpu_percent", "mem_percent", "threads"]])
        features = torch.tensor(scaled_features, dtype=torch.float32)
   
      
        sequences = create_sequences(features, seq_len=10)
        model = AE(input_shape=3, seq_len=10).to(device)
        criterion = torch.nn.MSELoss()
        optimizer = torch.optim.Adam(model.parameters(), lr=lr)

        for epoch in tqdm(range(epochs)):
            optimizer.zero_grad()
            reconstructed = model(sequences.to(device))
            loss = criterion(reconstructed, sequences.to(device))
            loss.backward()
            optimizer.step()
            if epoch % 50 == 0:
                print(f"Epoch {epoch}: Loss = {loss.item():.4f}")

        torch.save(model.state_dict(), os.path.join(save_path, "autoencoder.pth"))
    except Exception as e:
        print(f"Error training autoencoder: {e}")


def train_models(df_software, df_hardware, user):
    save_path = f"saved/{user}"
    os.makedirs(save_path, exist_ok=True)

    train_autoencoder(df_software, save_path)

    dbscan_model = train_dbscan(df_software)
    save_dbscan_model(dbscan_model, user)

    iforest_model = train_iforest(df_hardware)
    save_iforest_model(iforest_model, user)