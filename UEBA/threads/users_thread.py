import time
from influxdb.influx_reader import get_hardware_metrics, get_software_metrics
from ai.models.isolation_forest import detect_anomalies_iforest,load_iforest_model
from ai.models.dbscan import load_dbscan_model, detect_anomalies_dbscan
from ai.models.autoencoder import detect_anomalies_autoencoder, load_autoencoder_model

# import sys
# import os
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# Check trainging process



def monitor_user(bucket, hostname):
    
    iforest_model = load_iforest_model(hostname)
    dbscan_model = load_dbscan_model(hostname)
    autoencoder_model = load_autoencoder_model(hostname)

    while True:
        hardware_metrics = get_hardware_metrics(bucket, hostname, time_range="-10s")
        software_metrics = get_software_metrics(bucket, hostname, time_range="-10s")
        auto, encoder = detect_anomalies_autoencoder(autoencoder_model, software_metrics)
        iforest = detect_anomalies_iforest(hardware_metrics, iforest_model)
        dbscan = detect_anomalies_dbscan(software_metrics, dbscan_model)
        
        print("From auto: ", auto,encoder)
        print("Fron iforest: ", iforest)
        print("From dbscan: ",dbscan)
         
        time.sleep(5)
     
    