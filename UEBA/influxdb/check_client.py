import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
import os
import time
import logging
from dotenv import load_dotenv

load_dotenv()


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s", filename="ueba.log")

def connect_to_influx():

    tries_count = 5
    wait_time = 60

    for count in range(1, tries_count + 1):
        try:
            client = influxdb_client.InfluxDBClient(
                url="http://localhost:8086",
                token=os.getenv("INFLUX_TOKEN"),
                org=os.getenv("INFLUX_ORG")
            )
            if client.ping():
                logging.info("Connected to InfluxDB successfully.")
                return client
            else:
                raise ConnectionError(f"Connection failed in attempt {count}")
        
        except Exception as e:
            logging.error(f"Unsuccessful request: {e}")
            if count < tries_count:
                wait = wait_time * count
                logging.info(f"Retrying in {wait} seconds")
                time.sleep(wait)

    logging.critical("All connection attempts to InfluxDB failed.")
    return None


client = connect_to_influx()
if client is None:
    logging.critical("Failed to connect to InfluxDB")
    exit(1)

query_api = client.query_api()
write_api = client.write_api(write_options=SYNCHRONOUS)
