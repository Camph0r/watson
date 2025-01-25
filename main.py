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


tables = query_api.query(
    'from(bucket:"mininet") '
    '|> range(start: -10d) '
    '|> filter(fn: (r) => r._field == "hardwareMetrics") '
    '|> filter(fn: (r) => r.hostname == "Camph0r")'
)
records = []
for table in tables:
    for row in table.records:
        values = row.values
        record = json.loads(values["_value"]) 
        record["_time"] = values["_time"] 
        records.append(record)
df = pd.DataFrame(records)

# Network data is ignored for now, will update later
features = df[["cpu_usage", "disk_usage", "memory_usage", "swap"]]
baseline = features.iloc[:15]  
detection = features.iloc[15:]
detection.count()
import matplotlib.pyplot as plt
import seaborn as sns


detection["_time"] = pd.to_datetime(df["_time"].iloc[10:])


plt.figure(figsize=(14, 8))


plt.subplot(2, 2, 1)
sns.lineplot(x="_time", y="cpu_usage", data=detection, label="CPU Usage", marker="*")
anomalies = detection[detection["anomaly"] == -1]
plt.scatter(anomalies["_time"], anomalies["cpu_usage"], color="red", label="Anomalies")
plt.title("CPU Usage Over Time")
plt.xlabel("Time")
plt.ylabel("CPU Usage (%)")
plt.legend()


plt.subplot(2, 2, 2)
sns.lineplot(x="_time", y="disk_usage", data=detection, label="Disk Usage", marker="*")
plt.scatter(anomalies["_time"], anomalies["disk_usage"], color="red", label="Anomalies")
plt.title("Disk Usage Over Time")
plt.xlabel("Time")
plt.ylabel("Disk Usage (%)")
plt.legend()


plt.subplot(2, 2, 3)
sns.lineplot(x="_time", y="memory_usage", data=detection, label="Memory Usage", marker="*")
plt.scatter(anomalies["_time"], anomalies["memory_usage"], color="red", label="Anomalies")
plt.title("Memory Usage Over Time")
plt.xlabel("Time")
plt.ylabel("Memory Usage (%)")
plt.legend()

plt.subplot(2, 2, 4)
sns.lineplot(x="_time", y="swap", data=detection, label="Swap Usage", marker="*")
plt.scatter(anomalies["_time"], anomalies["swap"], color="red", label="Anomalies")
plt.title("Swap Usage Over Time")
plt.xlabel("Time")
plt.ylabel("Swap Usage (%)")
plt.legend()

plt.tight_layout()
plt.show()