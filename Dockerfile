FROM python:alpine

COPY ./repeqtt.py repeqtt.py

RUN pip install paho-mqtt 

CMD python repeqtt.py