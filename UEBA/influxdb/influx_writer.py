import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
import os

from dotenv import load_dotenv



load_dotenv()

client = influxdb_client.InfluxDBClient(url="http://localhost:8086", token=os.getenv("INFLUX_TOKEN"), org=os.getenv("INFLUX_ORG"))
write_api = client.write_api(write_options=SYNCHRONOUS)

def write_hw_anomalies(df, hostname):
    

    row = df.iloc[0]
    severity = "severe" if row["anomaly"] == -1 else "normal"

    point = influxdb_client.Point("anomaly_detection") \
    .tag("hostname", hostname) \
    .tag("anomaly_type", "hardware") \
    .field("cpu_usage", row["cpu_usage"]) \
    .field("disk_usage", row["disk_usage"]) \
    .field("memory_usage", row["memory_usage"]) \
    .field("swap", row["swap"]) \
    .field("packetsSent", row["packetsSent"]) \
    .field("packetsRecv", row["packetsRecv"]) \
    .tag("severity", severity) \
    .time(row["_time"])
    
    write_api.write(bucket="anomalies", org=os.getenv("INFLUX_ORG"), record=point)
    write_api.close()

def write_sw_anomalies(df, hostname):
    

    row = df.iloc[0]
    severity = "severe" if row["anomaly"] == -1 else "normal"

    point = influxdb_client.Point("anomaly_detection") \
    .tag("hostname", hostname) \
    .tag("anomaly_type", "software") \
    .field("cpu_percent", row["cpu_percent"]) \
    .field("mem_percent", row["mem_percent"]) \
    .field("threads_count", row["threads"]) \
    .field("process-created", row["created"].isoformat()) \
    .tag("severity", severity) \
    .time(row["_time"])
    write_api.write(bucket="anomalies", org=os.getenv("INFLUX_ORG"), record=point)
    write_api.close()