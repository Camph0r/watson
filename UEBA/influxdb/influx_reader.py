import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
import json
import os
import pandas as pd
from dotenv import load_dotenv
import logging
from influxdb.check_client import query_api

load_dotenv()

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, datefmt=DATE_FORMAT)


def query_metrics(bucket, hostname, metric_type, time_range="-5d"):
    query = f"""
    from(bucket:"{bucket}")
    |> range(start: {time_range})
    |> filter(fn: (r) => r._field == "{metric_type}")
    |> filter(fn: (r) => r.hostname == "{hostname}")
    """
    try:
        tables = query_api.query(query)
        if len(tables) > 0:
            return tables
        else:
            raise ValueError(f"No data found for {metric_type} for {hostname}")
    except Exception as e:
        logging.warning(f"Failed to query {metric_type} for {hostname}: {e}")
        return None


def get_software_metrics(bucket, hostname, time_range="-5d"):
    tables = query_metrics(bucket, hostname, "softwareMetrics", time_range)
    if tables is None:
        return None
    records = []
    for table in tables:
        for row in table.records:
            values = row.values
            record = json.loads(values["_value"])
            df = pd.DataFrame(record)
            df["created"] = pd.to_datetime(df["created"])
            df["_time"] = values["_time"]
            df = df.drop(columns=["score"], errors="ignore")
            #df = df.sort_values("cpu_percent", ascending=False).head(20)
            records.append(df)

    return records


def fetch_live_metrics(bucket, hostname, time_range="-10s"):
    tables = query_metrics(bucket, hostname, "softwareMetrics", time_range)
    if tables is None:
        return None
    records = []
    for table in tables:
        for row in table.records:
            values = row.values
            record = json.loads(values["_value"])
            record = pd.DataFrame(record)
            record["created"] = pd.to_datetime(record["created"])
            record = record.drop(columns=["score"], errors="ignore")
            record["_time"] = values["_time"]
            records.append(record)
    df = pd.concat(records).reset_index(drop=True)
    return df


def get_hardware_metrics(bucket, hostname, time_range="-5d"):
    tables = query_metrics(bucket, hostname, "hardwareMetrics", time_range)
    if tables is None:
        return None
    records = []
    for table in tables:
        for row in table.records:
            values = row.values
            record = json.loads(values["_value"])

            record["_time"] = values["_time"]
            records.append(record)
    records = pd.DataFrame(records)

    records["packetsSent"] = records["network"].apply(lambda x: x["packetsSent"])
    records["packetsRecv"] = records["network"].apply(lambda x: x["packetsRecv"])
    records = records.drop(columns=["network"], errors="ignore", axis=1)

    return records
