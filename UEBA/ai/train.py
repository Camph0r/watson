import torch
from tqdm import tqdm
from models.autoencoder import AE

from models.isolation_forest import save_iforest_model, train_iforest
from sklearn.preprocessing import StandardScaler
import logging
import sys
import os

import json
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from influxdb.influx_reader import get_software_metrics, get_hardware_metrics

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging(level=logging.INFO):
    logging.basicConfig(level=level, format=LOG_FORMAT, datefmt=DATE_FORMAT)


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def create_sequences(df_list, seq_len):
    sequences = []
    df_list = [df for df in df_list if len(df) == 20]

    for i in range(len(df_list) - seq_len + 1):
        chunk = df_list[i : i + seq_len]

        scaled_chunk_tensors = []
        for df in chunk:
            scaler = StandardScaler()
            scaled = scaler.fit_transform(df[["cpu_percent", "mem_percent", "threads"]])
            tensor = torch.tensor(scaled, dtype=torch.float32)
            scaled_chunk_tensors.append(tensor)

        sequence_tensor = torch.stack(scaled_chunk_tensors)  # shape (10, 20, 3)
        sequences.append(sequence_tensor)
    return torch.stack(sequences)


def train_autoencoder(df, save_path, epochs=1000, lr=0.001):
    try:

        sequences = create_sequences(df, seq_len=10)
        sequences = sequences.view(sequences.shape[0], sequences.shape[1], -1)

        model = AE(input_shape=60, seq_len=10).to(device)
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
        logging.info(f"Model saved successfully to {save_path}/autoencoder.pth")
    except Exception as e:
        logging.error(f"Error training autoencoder: {e}")


def train_models(df_software, df_hardware, user):
    save_path = f"saved/{user}"
    os.makedirs(save_path, exist_ok=True)

    train_autoencoder(df_software, save_path)

    iforest_model = train_iforest(df_hardware)
    save_iforest_model(iforest_model, user)


# load_dotenv()
# USERS = json.loads(os.getenv("USERS"))
# software = get_software_metrics("mininet", USERS[0], time_range="-3d")
# hardware = get_hardware_metrics("mininet", USERS[0], time_range="-3d")
# train_models(software, hardware, USERS[0])
