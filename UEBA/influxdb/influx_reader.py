import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
import json
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

client = influxdb_client.InfluxDBClient(url="http://localhost:8086", token=os.getenv("INFLUX_TOKEN"), org=os.getenv("INFLUX_ORG"))
query_api = client.query_api()
def query_metrics(bucket, hostname, metric_type, time_range="-5d"):
    query = f'''
    from(bucket:"{bucket}")
    |> range(start: {time_range})
    |> filter(fn: (r) => r._field == "{metric_type}")
    |> filter(fn: (r) => r.hostname == "{hostname}")
    '''
    tables = query_api.query(query)
    return tables

def get_software_metrics(bucket, hostname, time_range="-5d"):
    tables = query_metrics(bucket, hostname, "softwareMetrics", time_range)
    records = []
    for table in tables:
        for row in table.records:
            values = row.values
            record = json.loads(values["_value"]) 
            record = pd.DataFrame(record)
            record["created"] = pd.to_datetime(record['created'])  
            record = record.drop(columns=["score"], errors="ignore")
            record["_time"] = values["_time"] 
            records.append(record)                                                                     

    df = pd.concat(records).reset_index(drop=True)
    return df


def get_hardware_metrics(bucket, hostname, time_range="-5d"):
    tables = query_metrics(bucket, hostname, "hardwareMetrics", time_range)
    records = []
    for table in tables:
        for row in table.records:
            values = row.values
            record = json.loads(values["_value"])
            
      
            record['_time'] = values['_time']

            records.append(record)
    records = pd.DataFrame(records)
    
    records['packetsSent'] = records['network'].apply(lambda x: x['packetsSent'])
    records['packetsRecv'] = records['network'].apply(lambda x: x['packetsRecv'])
    records = records.drop(columns=['network'],errors='ignore',axis=1) 
    
    return records