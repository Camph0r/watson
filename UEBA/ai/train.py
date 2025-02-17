import torch
import torch.nn as nn
from tqdm import tqdm
from models.autoencoder import AE
from models.dbscan import train_dbscan, save_dbscan_model
from models.isolation_forest import save_iforest_model, train_iforest
import sys
import os
import logging

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# from influxdb.influx_reader import get_software_metrics, get_hardware_metrics

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="ueba.log",
)


def train_autoencoder(df, save_path, epochs=100, lr=0.01):
    try:
        model = AE(input_shape=3).to(device)
        criterion = torch.nn.MSELoss()
        optimizer = torch.optim.Adam(model.parameters(), lr=lr)
        features = df[["cpu_percent", "mem_percent", "threads"]].values
        features = torch.tensor(features, dtype=torch.float32)
        for epoch in tqdm(range(epochs)):
            optimizer.zero_grad()
            reconstructed = model(features)
            loss = criterion(reconstructed, features)
            loss.backward()
            optimizer.step()
            if epoch % 10 == 0:
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
