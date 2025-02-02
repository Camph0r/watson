import torch
import torch.nn as nn
from tqdm import tqdm
from models.autoencoder import AE
from models.dbscan import train_dbscan, save_dbscan_model
from models.isolation_forest import save_iforest_model, train_iforest
## Remember to remove later
import sys
import os
from influxdb.influx_reader import get_hardware_metrics, get_software_metrics

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")






def train_autoencoder(df, save_path,epochs=100, lr=0.001):
    model = AE(input_shape=3).to(device)
    criterion = torch.nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    features = df[['cpu_percent', 'mem_percent', 'threads']].values
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


def train_models(df_software,df_hardware, user):
    save_path = f"saved/{user}"
    os.makedirs(save_path, exist_ok=True) 
  
    train_autoencoder(df_software, save_path)

    dbscan_model = train_dbscan(df_software)
    save_dbscan_model(dbscan_model, user)

    iforest_model = train_iforest(df_hardware)
    save_iforest_model(iforest_model, user)

hardware = get_hardware_metrics("mininet", "Camph0r")
software = get_software_metrics("mininet", "Camph0r")

train_models(software,hardware , "Camph0r")