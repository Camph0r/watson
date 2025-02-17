import threading
from threads.users_thread import monitor_user
from dotenv import load_dotenv
import sys
import os
import json
import time
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="ueba.log",
)
load_dotenv()
INFLUX_BUCKET = os.getenv("INFLUX_BUCKET")
USERS = json.loads(os.getenv("USERS"))


def run_thread():

    threads = {}
    for user in USERS:
        thread = threading.Thread(target=monitor_user, args=(INFLUX_BUCKET, user))
        thread.daemon = True
        thread.start()
        threads[user] = thread
    while True:
        try:
            time.sleep(5)
            for user, thread in threads.items():

                if not thread.is_alive():
                    logging.warning(f"Restarting thread for '{user}'")
                #    new_thread = threading.Thread(target=monitor_user, args=(INFLUX_BUCKET, user))
                #    new_thread.daemon = True
                #    new_thread.start()
                #    threads[user] = new_thread
        except KeyboardInterrupt as e:
            logging.info("Exiting the program")
            sys.exit(0)
        except Exception as e:
            logging.error(e)
            time.sleep(5)
