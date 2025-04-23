import threading
from threads.users_thread import monitor_user
from dotenv import load_dotenv
import sys
import os
import json
import time
import logging


logger = logging.getLogger(__name__)
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
                    logger.warning(f"Restarting thread for '{user}'")
                #    new_thread = threading.Thread(target=monitor_user, args=(INFLUX_BUCKET, user))
                #    new_thread.daemon = True
                #    new_thread.start()
                #    threads[user] = new_thread
        except KeyboardInterrupt as e:
            logger.info("Exiting the program")
            sys.exit(0)
        except Exception as e:
            logger.error(e)
            time.sleep(5)
