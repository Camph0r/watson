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

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
## NEED TO FIX DIMENSION RELATED ERRORS
# Try direct checking of host status


def monitor_user(bucket, hostname):

    try:
        iforest_model = load_iforest_model(hostname)
        autoencoder_model = load_autoencoder_model(hostname)
        autoencoder_model.eval()
        scaler = StandardScaler()
        
        buffer = deque(maxlen=10)
        buffer_index = deque(maxlen=10)
    except Exception as e:
        logging.error(e)
        return

    while True:
        try:
            hardware_metrics = get_hardware_metrics(bucket, hostname, time_range="-7s")
            software_metrics = get_software_metrics(bucket, hostname, time_range="-7s")
            if software_metrics.empty:
                time.sleep(2)
                continue
            iforest = detect_anomalies_iforest(hardware_metrics, iforest_model)
            write_hw_anomalies(iforest, hostname)
            values = software_metrics[["cpu_percent", "mem_percent", "threads"]].values
       
            buffer.extend(values)
            buffer_index.extend(software_metrics.index)

            if len(buffer) == 10:
                sequence = np.array(buffer)
                scaler = StandardScaler()
                scaled_seq = scaler.fit_transform(sequence)
                seq_tensor = torch.tensor(np.array(scaled_seq).reshape(1, 10, 3), dtype=torch.float32)
                loss, is_anomaly = detect_anomalies_autoencoder(autoencoder_model, seq_tensor)

                index = list(buffer_index)[-1:]
                sw_df = pd.DataFrame(index=index)
                sw_df["reconstruction_error"] = loss
                sw_df["is_anomaly"] = is_anomaly

                write_sw_anomalies(sw_df, hostname)
            
       
            
            # process_anomaly_detection(software_metrics, hostname)
            time.sleep(5)
        except Exception as e:
            logging.warning(f"While monitoring {hostname}: {e}")
            time.sleep(5)
