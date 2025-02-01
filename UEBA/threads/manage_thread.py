import threading
from threads.user_thread import monitor_user

## For time being, hardcoding the users, later use influx to get uses (host)
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