import threading
import time
import pandas as pd
from influxdb.influx_reader import query_metrics
from models.isolation_forest import train_isolation_forest, detect_anomalies

def monitor_user(bucket, hostname):
    records = query_metrics(bucket, hostname, metrics="harwareMetrics")
    df = pd.DataFrame(records)
    baseline = df[["cpu_usage", "disk_usage", "memory_usage", "swap"]].iloc[:100]
    model = train_isolation_forest(baseline) ## will change to save the model
    while True:
        new_records = query_metrics(bucket, hostname, time_range="-5s")
        if new_records:
            detection = pd.DataFrame(new_records)
            anomalies = detect_anomalies(model, detection)
            if not anomalies.empty: ## Later save as log and alert
                print(f"Warning: Malicious metric detected at {anomalies['_time'].iloc[-1]} in host {hostname}")
        time.sleep(5)
     
    