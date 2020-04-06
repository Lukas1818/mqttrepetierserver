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
            topic = config['broker']['root_topic']
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
        
alltopics = []
srvdata = []
topic = ""
auth = {}
brok = ""

try:
    config = configparser.ConfigParser()
    config.read('repeqtt.conf')
except:
    print("Error Reading Configuration File",sys.exc_info())
else:   
    while True:
        alltopics = []
        srvdata = []
        data = []
        queryRepetier()
        for k in range(0,len(alltopics)):
            publish.single(alltopics[k].topic.lower(), alltopics[k].value, auth=auth, hostname=config['broker']['address'])
        time.sleep(int(config['broker']['update_interval']))
