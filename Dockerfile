FROM python:alpine

COPY ./repeqtt.py repeqtt.py

RUN pip install --no-cache-dir paho-mqtt

CMD python repeqtt.py
