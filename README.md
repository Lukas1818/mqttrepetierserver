# mqttrepetierserver
a mqtt client for repetier host via rest api

Functions: Reads, parses and trasforms into mqtt topics and publish server and printers informations taken from repetier rest api. Create OPENHAB2 things, items and stimap files

Prerequisites: Repetier Server with rest api enabled. A machine with python 3.7 and paho.mqtt (it can be any kind of hw supporing python (i tested it on windows and debian machines)

Installation: copy repeqtt.py and repeqtt.conf in a directory optionally you can add a cron schedule on linux or ar scheduled job on windows

Running for the first time: launch python repeqtt.py, it has 2 command line options: -f only create openhab files -b create broker definition in repetier.things file, only if also -f is specified on command line. It will create 3 files, you can place them into the appropiate directory under openhab

Running: launch python repeqtt.py optionally on linux you can create a cron job to start the script every x seconds/minutes/hours tha same on windows.

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

bridge = yourbridge <------ openhab2 bridge name (see notes)

keepalive = 30000 <------ broker configuration parameters

reconnect = 60000

qos = 0

secure = false

retain = false

clientID = mqttReptierClient

root_topic = 3dprinters <------- root topic for items

notes: if you already have an mqtt broker bridge defined in openhab please do use -b option and fill broker parameters with the same parameters used in the things file you already have. in other words use -b option only if this is the first mqtt bridge you are defining in openhab2
