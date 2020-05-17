#!/usr/bin/env python
import paho.mqtt.client as mqtt
import sys
import time
import os


LOCAL_MQTT_HOST  = "tx2_broker"
LOCAL_MQTT_PORT  = 1883
LOCAL_MQTT_TOPIC = "video/face"

REMOTE_MQTT_HOST  = os.environ['REMOTE_HOST']
REMOTE_MQTT_PORT  = 1883
REMOTE_MQTT_TOPIC = "video/face"


def on_connect_local(client, userdata, flags, rc):
       print("Connected local ", rc)
       if rc==0:
           print("local connected OK Returned code=",rc)
       else:
           print("local Bad connection Returned code= ",rc)

def on_connect_remote(client, userdata, flags, rc):
       print("Connected remote ", rc)
       if rc==0:
           print("remote connected OK Returned code=",rc)
       else:
           print("remote Bad connection Returned code= ",rc)
	
def on_message(client,userdata, msg):
  try:
    print("message received from local, no of bytes : ", sys.getsizeof(msg.payload))	

    # republish.
    remote_mqttclient.publish(REMOTE_MQTT_TOPIC, payload=msg.payload, qos=0, retain=False)
  except:
    print("Unexpected error:", sys.exc_info()[0])


local_mqttclient = mqtt.Client()
local_mqttclient.on_connect = on_connect_local
local_mqttclient.on_message = on_message


while True:
   try:
        local_mqttclient.connect(LOCAL_MQTT_HOST, LOCAL_MQTT_PORT, 60)
   except:
       print("local connect failed : ", str(LOCAL_MQTT_HOST) + ":" +  str(LOCAL_MQTT_PORT), " ...will retry")
       time.sleep(3)
   else: break

# go into a loop
local_mqttclient.loop_start()

remote_mqttclient = mqtt.Client()
remote_mqttclient.connected_flag = False
remote_mqttclient.on_connect = on_connect_remote

while True:
   try:
        remote_mqttclient.connect(REMOTE_MQTT_HOST, REMOTE_MQTT_PORT, 60)
   except:
       print("remote connect failed : ", str(REMOTE_MQTT_HOST) + ":" + str(REMOTE_MQTT_PORT), " ...will retry")
       time.sleep(3)
   else: break


# go into a loop
remote_mqttclient.loop_start()

local_mqttclient.subscribe(LOCAL_MQTT_TOPIC)


try:
   while True:
      time.sleep(1)

# if the user presses control-c to quit, stop the MQTT loop
except KeyboardInterrupt:
   local_mqttclient.loop_stop()
   remote_mqttclient.loop_stop()
   pass 
