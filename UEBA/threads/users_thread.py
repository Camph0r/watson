import time
from influxdb.influx_reader import get_hardware_metrics, get_software_metrics
from ai.models.isolation_forest import detect_anomalies_iforest, load_iforest_model
from ai.models.autoencoder import detect_anomalies_autoencoder, load_autoencoder_model
import pandas as pd
from influxdb.influx_writer import write_hw_anomalies, write_sw_anomalies
import logging
from collections import deque
import torch
from sklearn.preprocessing import StandardScaler
import numpy as np

# from utils.preprocess import process_anomaly_detection


logger = logging.getLogger(__name__)
# NEED TO SAVE SCALER FOR EACH USER
# Try direct checking of host status


def monitor_user(bucket, hostname):

    try:
        iforest_model = load_iforest_model(hostname)
        autoencoder_model = load_autoencoder_model(hostname)
        autoencoder_model.eval()
        scaler = StandardScaler()

        buffer = deque(maxlen=10)

    except Exception as e:
        logger.error(e)
        return

    while True:
        try:

            hardware_metrics = get_hardware_metrics(bucket, hostname, time_range="-7s")
            software_metrics = get_software_metrics(bucket, hostname, time_range="-7s")

            iforest = detect_anomalies_iforest(hardware_metrics, iforest_model)
            write_hw_anomalies(iforest, hostname)

            scaled = scaler.transform(
                software_metrics[["cpu_percent", "mem_percent", "threads"]]
            )
            reshaped = scaled.reshape(-1)  # Shape (60,)
            buffer.append(reshaped)

            if len(buffer) == 10:
                sequence = np.array(buffer).reshape(1, 10, 60)

                torch_seq = torch.tensor(sequence, dtype=torch.float32)

                loss, is_anomaly = detect_anomalies_autoencoder(
                    autoencoder_model, torch_seq
                )
                print(f"Loss: {loss:.6f}, Anomaly: {bool(is_anomaly)}")

            # process_anomaly_detection(software_metrics, hostname)
            time.sleep(5)
        except Exception as e:
            logger.warning(f"While monitoring {hostname}: {e}")
            time.sleep(5)
