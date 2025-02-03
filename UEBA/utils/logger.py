import logging
from datetime import datetime

logging.basicConfig(filename="anomalies.log", level=logging.INFO, format="%(message)s")

def log_anomaly(anomaly_type, hostname, severity, details):
    log_entry = f"{datetime.now().isoformat()} {anomaly_type} {hostname} {severity} {details}"
    logging.info(log_entry)