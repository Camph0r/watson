FROM python:3.10-slim

WORKDIR /ueba

COPY requirements.txt /ueba/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt


COPY ai /ueba/ai
COPY influxdb /ueba/influxdb
COPY threads /ueba/threads
COPY utils /ueba/utils
COPY main.py /ueba/main.py




CMD ["python", "main.py"]