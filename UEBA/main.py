import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
from sklearn.ensemble import IsolationForest
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json
from dotenv import load_dotenv
import os
load_dotenv()
bucket = "mininet"

client = influxdb_client.InfluxDBClient(url="http://localhost:8086", token=os.getenv("TOKEN"), org="docs")

write_api = client.write_api(write_options=SYNCHRONOUS)
query_api = client.query_api()


def monitor_user(bucket, hostname):
    query = f'''
    from(bucket:"{bucket}")
    |> range(start: -1d)
    |> filter(fn: (r) => r._field == "hardwareMetrics")
    |> filter(fn: (r) => r.hostname == "{hostname}")
    '''
    tables = query_api.query(query)
    records = []
    for table in tables:
        for row in table.records:
            values = row.values
            record = json.loads(values["_value"])
            record["_time"] = values["_time"]
            records.append(record)

    df = pd.DataFrame(records)
    # Still network data is ignored for now, will update later
    baseline = df[["cpu_usage", "disk_usage", "memory_usage", "swap"]].iloc[:15]
    model = IsolationForest(n_estimators=100, contamination=0.1, random_state=42)
    model.fit(baseline)
    
    while True:
        new_data = query_api.query(f'''
        from(bucket:"{bucket}")
        |> range(start: -5s)
        |> filter(fn: (r) => r._field == "hardwareMetrics")
        |> filter(fn: (r) => r.hostname == "{hostname}")
        ''')
        new_records = []
        for table in new_data:
            for row in table.records:
                values = row.values
                record = json.loads(values["_value"])
                record["_time"] = values["_time"]
                new_records.append(record)
        
        if new_records:
            detection = pd.DataFrame(new_records)
            features = detection[["cpu_usage", "disk_usage", "memory_usage", "swap"]]
            detection["anomaly"] = model.predict(features)
            
            anomalies = detection[detection["anomaly"] == -1]
            print(anomalies, hostname)

            if not anomalies.empty:
                print(f"Warning: Malicious metric detected at {anomalies['_time'].iloc[-1]} in host {hostname}")
        time.sleep(5)

users = [
    {"bucket": "mininet", "hostname": "Camph0r"},
    {"bucket": "mininet", "hostname": "mininet-vm"}
]

threads = []
for user in users:
    thread = threading.Thread(target=monitor_user, args=(user["bucket"], user["hostname"]))
    thread.start()
    threads.append(thread)

for thread in threads:
    thread.join()