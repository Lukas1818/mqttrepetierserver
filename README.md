# mqttrepetierserver
a mqtt client for repetier host via rest api

Functions: Reads, parses and trasforms into mqtt topics and publish server and printers informations taken from repetier rest api. Create OPENHAB2 things, items and stimap files

Prerequisites: Repetier Server with rest api enabled. A machine with python 3.7 and paho.mqtt (it can be any kind of hw supporing python (i tested it on windows and debian machines)

Installation: copy repeqtt.py and repeqtt.conf in a directory optionally you can add a cron schedule on linux or ar scheduled job on windows

REPEQTT.CONF this is the configuration files, it uses an ini like structure:

[upsqtt]

name=repeqtt

[server]

address = 10.11.12.13 <---- address of the machine running repetier server

port = 6969 <---- repetier webserver port

user = admin <---- repetier webserver auth user

secret = palabrasegreta <--- repetier webserver password

[broker]

address = broker.example.com <------ broker address

port = 1833 <------ broker port

user = mqttUser <------ broker user

secret = palabrasegreta2 <------ broker password

root_topic = 3dprinters <------- root topic for items

update_interval = 15 <------- update the mqtt-broker every x seconds
