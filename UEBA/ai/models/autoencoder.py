import torch
import torch.nn as nn
import numpy as np
import os
from tqdm import tqdm

# try huber loss later

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

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
    

def load_autoencoder_model(user):
    model = AE(input_shape=3)
    model_path = f"saved/{user}/autoencoder.pth"
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"No model found for user: {user}")
    model.load_state_dict(torch.load(model_path))
    model.eval()
    return model

def detect_anomalies_autoencoder(model, detection_data):
    if detection_data is None:
        return None, None
    features = detection_data[['cpu_percent', 'mem_percent', 'threads']].values
    features = torch.tensor(features, dtype=torch.float32)
 
    
    with torch.no_grad():
        reconstructed = model(features)
        loss = torch.mean((features - reconstructed) ** 2, dim=1).numpy()

    threshold = np.mean(loss) + 3 * np.std(loss)  
    return loss, loss > threshold
