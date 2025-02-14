import influxdb_client
import os
import logging
from influxdb.check_client import write_api
from dotenv import load_dotenv

load_dotenv()
BUCKET = os.getenv("INFLUX_WRITE_BUCKET")
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s", filename="ueba.log")

def write_hw_anomalies(df, hostname):
    if df.empty:
      logging.warning(f"No hardware data available to write for {hostname}")
      return
    
    
    
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
    try:
      write_api.write(bucket="anomalies", org=os.getenv("INFLUX_ORG"), record=point)
      write_api.close()
    except Exception as e:
     logging.error(f"Failed to write anomaly data: {e}")

def write_sw_anomalies(df, hostname):

  if df.empty:
    logging.warning(f"No software data available to write for {hostname}")
    return
    
    

  row = df.iloc[0]
  severity = "severe" if row["anomaly"] == -1 else "normal"
  point = influxdb_client.Point("anomaly_detection") \
  .tag("hostname", hostname) \
  .tag("anomaly_type", "software") \
  .field("cpu_percent", row["cpu_percent"]) \
  .field("mem_percent", row["mem_percent"]) \
  .field("threads_count", row["threads"]) \
  .field("process-created", row["created"].isoformat()) \
  .field("reconstruction_error", row["reconstruction_error"]) \
  .tag("severity", severity) \
  .time(row["_time"])
  try:
    write_api.write(bucket="anomalies", org=os.getenv("INFLUX_ORG"), record=point)
    write_api.close()
  except Exception as e:
    logging.error(f"Failed to write anomaly data: {e}")