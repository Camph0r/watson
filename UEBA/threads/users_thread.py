import time
from influxdb.influx_reader import get_hardware_metrics, get_software_metrics
from ai.models.isolation_forest import detect_anomalies_iforest, load_iforest_model
from ai.models.dbscan import load_dbscan_model, detect_anomalies_dbscan
from ai.models.autoencoder import detect_anomalies_autoencoder, load_autoencoder_model
import pandas as pd
from influxdb.influx_writer import write_hw_anomalies, write_sw_anomalies
import logging

# from utils.preprocess import process_anomaly_detection

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Try direct checking of host status


def monitor_user(bucket, hostname):

    try:
        iforest_model = load_iforest_model(hostname)
        # dbscan_model = load_dbscan_model(hostname)
        autoencoder_model = load_autoencoder_model(hostname)
    except Exception as e:
        logging.error(e)
        return

    while True:
        try:
            hardware_metrics = get_hardware_metrics(bucket, hostname, time_range="-7s")
            software_metrics = get_software_metrics(bucket, hostname, time_range="-7s")
            autoencoder = detect_anomalies_autoencoder(
                autoencoder_model, software_metrics
            )
            software_metrics["reconstruction_error"] = pd.Series(
                autoencoder[0], index=software_metrics.index
            )
            software_metrics["is_anomaly"] = pd.Series(
                autoencoder[1], index=software_metrics.index
            )
            iforest = detect_anomalies_iforest(hardware_metrics, iforest_model)
            # dbscan = detect_anomalies_dbscan(software_metrics, dbscan_model)
            write_hw_anomalies(iforest, hostname)

            write_sw_anomalies(software_metrics, hostname)
            # process_anomaly_detection(software_metrics, hostname)

            time.sleep(5)
        except Exception as e:
            logging.warning(f"While monitoring {hostname}: {e}")
            time.sleep(5)
