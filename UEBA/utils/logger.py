import logging
from datetime import datetime


LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging(level=logging.INFO):
    logging.basicConfig(level=level, format=LOG_FORMAT, datefmt=DATE_FORMAT)


anomaly_logger = logging.getLogger("anomaly_logger")

if not anomaly_logger.hasHandlers():
    anomaly_handler = logging.FileHandler("anomalies.log")
    anomaly_handler.setFormatter(logging.Formatter("%(message)s"))
    anomaly_logger.addHandler(anomaly_handler)
    anomaly_logger.setLevel(logging.INFO)
    anomaly_logger.propagate = False


def log_anomaly(anomaly_type, hostname, severity, details):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    log_entry = f"{timestamp} {anomaly_type} {hostname} {severity} {details}"
    anomaly_logger.info(log_entry)
