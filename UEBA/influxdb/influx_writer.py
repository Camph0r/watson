import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
import os

from dotenv import load_dotenv



load_dotenv()

client = influxdb_client.InfluxDBClient(url="http://localhost:8086", token=os.getenv("INFLUX_TOKEN"), org=os.getenv("INFLUX_ORG"))
write_api = client.write_api(write_options=SYNCHRONOUS)

def write_anomalies_to_influx(df, hostname, anomaly_type):
    

    row = df.iloc[0]
    severity = "severe" if row["anomaly"] == -1 else "normal"

    point = influxdb_client.Point("anomaly_detection") \
    .tag("hostname", hostname) \
    .tag("anomaly_type", anomaly_type) \
    .field("cpu_usage", row["cpu_usage"]) \
    .field("disk_usage", row["disk_usage"]) \
    .field("memory_usage", row["memory_usage"]) \
    .field("swap", row["swap"]) \
    .field("packetsSent", row["packetsSent"]) \
    .field("packetsRecv", row["packetsRecv"]) \
    .field("anomaly", row["anomaly"]) \
    .tag("severity", severity) \
    .time(row["_time"])
    
    write_api.write(bucket="anomalies", org=os.getenv("INFLUX_ORG"), record=point)
    write_api.close()

