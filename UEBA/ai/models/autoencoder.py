import torch
import torch.nn as nn
import numpy as np
from tqdm import tqdm

# May require to tune the loss function and threshold value
# also need to fix the frequent loading of model
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
    



def detect_anomalies_autoencoder(model,user, detection_data):
    features = torch.tensor(detection_data, dtype=torch.float32)
    savedModel = AE(input_shape=features.shape[1])
    savedModel.load_state_dict(torch.load(f"model/autoencoder-{user}.pth"))
    savedModel.eval()
    with torch.no_grad():

        reconstructed = model(features)
        loss = torch.mean((features - reconstructed) ** 2, dim=1).numpy()
    threshold = np.mean(loss) + 2 * np.std(loss)  
    return loss, loss > threshold
