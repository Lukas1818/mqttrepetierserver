#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2019 aRGi <info@argi.mooo.com>
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Distribution License v1.0
# which accompanies this distribution.
#
# The Eclipse Distribution License is available at
#   http://www.eclipse.org/org/documents/edl-v10.php.
#
# Contributors:
#    aRGi Rob - initial implementation

# This is a MQTT client to publish REPETIER host printer data as topics.
# http://192.168.69.180:3344/printer/api/Anet_AR8?apikey=e117e5d6-2197-4e33-9588-27bfb2b66b8d&a=stateList&data={}

import configparser
import paho.mqtt.publish as publish
import urllib.request, json 
import sys
import argparse
import time
import re

class Topic:
    def __init__(self, path, val, type, broker):
        self.topic = path
        self.value = val
        self.type = type
        self.broker = broker
		
def json2topic(src, topic, broker): 
    for keys,values in src.items(): 
        if type(values) == dict:
            json2topic(values,topic + "/" + keys,broker)
        elif type(values) == list:
            i=0
            for items in values: 
                json2topic(items,topic + "/" + keys + str(i),broker)
                i=i+1
        else:
            if str(values).lower() == 'on' or str(values).lower() == 'true':
                values = 'CLOSED'
            else:
                if str(values).lower() == 'off' or str(values).lower() == 'false':
                    values = 'OPEN'
            alltopics.append(Topic(topic + "/" + keys, str(values),'',broker))

def queryRepetier():
    data = []
    global topic
    global auth
    global brok

    try:
        with urllib.request.urlopen("http://" + config['server']['address'] + ":" + config['server']['port'] + "/printer/info") as rooturl:
            srvdata = json.loads(str(rooturl.read().decode()))
            #topic = config['repeqtt']['name'] + "/" + srvdata['servername']
            topic = srvdata['servername']
            brok = config['repeqtt']['name']
            json2topic(srvdata, topic, brok)
    except:
        print("Error Reading Server configuration",sys.exc_info())
    else:
        serverName = srvdata['servername']
        serverKey = srvdata['apikey']
        auth = {'username':config['broker']['user'], 'password':config['broker']['secret']}

        try:
            with urllib.request.urlopen("http://" + config['server']['address'] + ":" + config['server']['port'] + "/printer/api?apikey=" + serverKey + "&a=stateList") as url:
               data = json.loads(str(url.read().decode()))
            json2topic(data, topic, brok)
            alltopics.append(Topic(topic + "/state","CLOSED",'', brok))
        except:
            alltopics.append(Topic(topic + "/state","OPEN",'', brok))


# create openhab files 
def openHabFiles(topics): 
    broker = "Bridge mqtt:broker:" + config['broker']['bridge'] + ' "MQTT broker bridge:' + config['broker']['bridge'] + '" @ "Home" [\n'
    broker += '\thost="' + config['broker']['address'] + '",\n'
    broker += '\tport=' + config['broker']['port'] + ',\n'
    broker += '\tsecure=' + config['broker']['secure'] + ',\n'
    broker += '\tretain=' + config['broker']['retain'] + ',\n'
    broker += '\tclientID="' + config['broker']['clientID'] + '",\n'
    broker += '\tkeepalive=' + config['broker']['keepalive'] + ',\n'
    broker += '\treconnect_time=' + config['broker']['reconnect'] + ',\n'
    broker += '\tusername="' + config['broker']['user'] + '",\n'
    broker += '\tpassword="' + config['broker']['secret'] + '"\n\t]\n'
    things = "\n\tThing mqtt:topic:" + config['broker']['bridge'] + ":" + config['broker']['root_topic'] + ' "Repetier Server" (mqtt:broker:' + config['broker']['bridge'] + ') @ "Home" {\n\t\tChannels:\n'

    for k in range(0,len(topics)):
        if topics[k].value.lower() == 'open' or topics[k].value.lower() == 'closed':
            type = 'Contact'
        else:
            if topics[k].value.lower().isdigit() or topics[k].value.lower().isnumeric():
                type = 'Number'
            else:
                try:
                    tstf = float(topics[k].value)
                    type = 'Number'
                except ValueError:
                    type = 'String'
        topics[k].type = type

    items = ''
    id = 0
    for k in range(0,len(topics)): 
        if topics[k].type.lower() == 'contact':
            items += topics[k].type.capitalize() + " 3DP_" + topics[k].topic.lower().replace("/","").replace("-","") + ' "' + topics[k].topic.replace("/"," ").capitalize() + ' [MAP(contact.map):%s]" <contact> { channel="mqtt:topic:' + config['broker']['bridge'] + ':' + config['broker']['root_topic'] + ':' + topics[k].topic.lower().replace("/","").replace("-","") + '" }\n'
        else:		
            items += topics[k].type.capitalize() + " 3DP_" + topics[k].topic.lower().replace("/","").replace("-","") + ' "' + topics[k].topic.replace("/"," ").capitalize() + ' [%s]" { channel="mqtt:topic:' + config['broker']['bridge'] + ':' + config['broker']['root_topic'] + ':' + topics[k].topic.lower().replace("/","").replace("-","")  + '" }\n'
        id += 1	   
	
    for k in range(0,len(topics)): 
       things += "\t\t\tType " + topics[k].type.lower() + ":" + topics[k].topic.lower().replace("/","").replace("-","") + ' "' + topics[k].topic.replace("-"," ").replace("/"," ") + '" [ stateTopic="' + topics[k].topic.lower() + '" ]\n'
    things += "\t}\n"
	
    maps = 'sitemap repetier label="3D Printers" {\n\tFrame label="' + config['broker']['root_topic'] + '" icon="poweroutlet_eu" {\n'
    for k in range(0,len(topics)): 
        maps += '\t\t'
        maps +=  "Text"
        maps += " item=3DP_" + topics[k].topic.lower().replace("/","").replace("-","") + '\n'
    maps += "\t}\n"
    maps += "}"
	
    try:
        f = open("repetier.things", "w")
        if parsedArgs.brokerdef:
           f.write(broker)
        f.write(things)
        f.close()
        f = open("repetier.items", "w")
        f.write(items)
        f.close()
        f = open("repetier.sitemap", "w")
        f.write(maps)
        f.close()
    except:
        print("Error Creating openhab configuration files.",sys.exc_info())

		
alltopics = []
srvdata = []
topic = ""
auth = {}
brok = ""

try:
    parser = argparse.ArgumentParser(description='Repetier Server data to MQTT topics')
    parser.add_argument('-f', action="store_true", default=False, dest="openhabfiles")
    parser.add_argument('-b', action="store_true", default=False, dest="brokerdef")
    parsedArgs = parser.parse_args()

    config = configparser.ConfigParser()
    config.read('repeqtt.conf')
except:
    print("Error Reading Configuration File",sys.exc_info())
else:
	
    if parsedArgs.openhabfiles:
        queryRepetier()
        openHabFiles(alltopics)
    else:
        while True:
            alltopics = []
            srvdata = []
            data = []
            queryRepetier()
            for k in range(0,len(alltopics)): 
                publish.single(alltopics[k].topic.lower(), alltopics[k].value, auth=auth, hostname=config['broker']['address'])
            time.sleep(15)
