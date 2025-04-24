import torch
import torch.nn as nn
import numpy as np
import os
import joblib

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


class AE(nn.Module):
    def __init__(self, **kwargs):
        super().__init__()
        input_dim = kwargs["input_shape"]
        seq_len = kwargs["seq_len"]
        latent_dim = 4
        hidden_dim = 16

        self.seq_len = seq_len
        self.input_dim = input_dim

        self.encoder_lstm = nn.LSTM(
            input_size=input_dim, hidden_size=hidden_dim, batch_first=True
        )
        self.encoder_fc = nn.Linear(hidden_dim, latent_dim)

        self.decoder_fc = nn.Linear(latent_dim, hidden_dim)
        self.decoder_lstm = nn.LSTM(
            input_size=hidden_dim, hidden_size=input_dim, batch_first=True
        )

    def forward(self, x):

        _, (h_n, _) = self.encoder_lstm(x)
        latent = self.encoder_fc(h_n[-1])  # [batch, latent_dim]

        repeated = self.decoder_fc(latent).unsqueeze(1).repeat(1, self.seq_len, 1)
        reconstructed, _ = self.decoder_lstm(repeated)
        return reconstructed


def load_autoencoder_model(user, input_shape=60, seq_len=10):
    model = AE(input_shape=input_shape, seq_len=seq_len).to(device)
    model_path = f"saved/{user}/autoencoder.pth"
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"No model found for user: {user}")
    model.load_state_dict(torch.load(model_path))
    model.eval()
    return model


def load_saved_scaler(hostname):

    return joblib.load(f"saved/{hostname}/scaler.pkl")

def detect_anomalies_autoencoder(model, torch_sequence):
    with torch.no_grad():
        reconstructed = model(torch_sequence)
        loss_tensor = torch.mean((torch_sequence - reconstructed) ** 2, dim=(1, 2))  # shape (1,)
        loss_value = loss_tensor.item()  

    threshold = 1.5
    is_anomaly = loss_value > threshold
    return loss_value, is_anomaly