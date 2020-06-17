#!/usr/bin/env python
import paho.mqtt.client as mqtt
import sys
import time
import pickle
import pathlib


LOCAL_MQTT_HOST  = "cloud_broker"
LOCAL_MQTT_PORT  = 1883
LOCAL_MQTT_TOPIC = "video/face"

def on_connect_local(client, userdata, flags, rc):
        print("connected to local broker with rc: " + str(rc))

def write_data_s3(root, directory, name, data):
    p = pathlib.Path(root + "/hw_faces/" + directory)
    p.mkdir(parents=True, exist_ok=True);

    # Write as binary
    with open(str(p/name), "wb+") as fp: fp.write(data)

def on_message(client,userdata, msg):
  try:
    decorded_msg = pickle.loads(msg.payload);
    file_name = decorded_msg['file']
    directory = decorded_msg['dir']
    img       = decorded_msg['data']

    print("message received from local, no of bytes : ", sys.getsizeof(msg.payload))	
    print("Image name : ", directory + "/" + file_name)
    write_data_s3('/mnt/drive0', directory, file_name, img)

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

local_mqttclient.subscribe(LOCAL_MQTT_TOPIC) # qos defaults to zero


try:
   while True:
      time.sleep(1)

# if the user presses control-c to quit, stop the MQTT loop
except KeyboardInterrupt:
   local_mqttclient.loop_stop()
   pass 
