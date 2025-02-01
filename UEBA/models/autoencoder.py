import torch
import torch.nn as nn
import numpy as np
from tqdm import tqdm

class AE(nn.Module):
    def __init__(self, **kwargs):
        super().__init__()
        self.encoder_hidden_layer = nn.Linear(
            in_features=kwargs["input_shape"], out_features=64
        )
        self.encoder_output_layer = nn.Linear(
            in_features=64, out_features=32
        )
        self.decoder_hidden_layer = nn.Linear(
            in_features=32, out_features=64
        )
        self.decoder_output_layer = nn.Linear(
            in_features=64, out_features=kwargs["input_shape"]
        )

    def forward(self, features):
        activation = self.encoder_hidden_layer(features)
        activation = torch.relu(activation)
        code = self.encoder_output_layer(activation)
        code = torch.relu(code)
        activation = self.decoder_hidden_layer(code)
        activation = torch.relu(activation)
        reconstructed = self.decoder_output_layer(activation)
        return reconstructed
    


def train_autoencoder(model, data, epochs=50, lr=0.001):
    criterion = torch.nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    features = torch.tensor(data, dtype=torch.float32)
    for epoch in tqdm(range(epochs)):
        optimizer.zero_grad()
        reconstructed = model(features)
        loss = criterion(reconstructed, features)
        loss.backward()
        optimizer.step()
        if epoch % 10 == 0:
            print(f"Epoch {epoch}: Loss = {loss.item():.4f}")


def detect_anomalies_autoencoder(model, detection_data):
    features = torch.tensor(detection_data, dtype=torch.float32)
    with torch.no_grad():
        reconstructed = model(features)
        loss = torch.mean((features - reconstructed) ** 2, dim=1).numpy()
    threshold = np.mean(loss) + 2 * np.std(loss)
    return loss, loss > threshold