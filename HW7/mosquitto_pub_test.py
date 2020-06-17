#!/usr/bin/env python3
import paho.mqtt.client as mqtt
import sys
import time
import pickle


MQTT_HOST  = "tx2_broker"
MQTT_PORT  = 1883
MQTT_TOPIC = "video/face"

def on_connect(client, userdata, flags, rc):
        print("connected to broker")

mqttclient = mqtt.Client()
mqttclient.on_connect = on_connect
mqttclient.connect(MQTT_HOST, MQTT_PORT, 60)

# go into a loop
mqttclient.loop_start()

to_send = {'file' : 'test3.txt', 'dir' : 'TEST', 'data' : 'Hello World'}

mqttclient.publish(MQTT_TOPIC, payload=pickle.dumps(to_send), qos=0, retain=False)

time.sleep(1)

mqttclient.loop_stop()

