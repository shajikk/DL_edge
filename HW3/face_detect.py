#!/usr/bin/env python3

import cv2
import numpy
import imutils
import time
from pathlib import Path
import paho.mqtt.client as mqtt
import sys
import pickle


# Debug mode (debug = 1), if debug is set,
# processes images will be saved in the local file system.
# It will not be sent over network Via MQTT.
debug = 0

# ------------------ Set up MQTT
MQTT_HOST  = "tx2_broker"
MQTT_PORT  = 1883
MQTT_TOPIC = "video/face"

def on_connect(client, userdata, flags, rc):
        print("connected to local broker")

mqttclient = mqtt.Client()
mqttclient.on_connect = on_connect

# Will wait here until the local MQTT tx2 brocker is up 
if not debug == 1 :
   while True:
      try:
           mqttclient.connect(MQTT_HOST, MQTT_PORT, 60)
      except:
          print("local connect failed : ", str(MQTT_HOST,) + ":" +  str(MQTT_PORT), " ...will retry")
          time.sleep(3)
      else: break
   
   # go into a loop
   mqttclient.loop_start()

# ------------------ OpenCV related settings

face_cascade = cv2.CascadeClassifier('/usr/share/OpenCV/haarcascades/haarcascade_frontalface_default.xml')

# Rescale the the frames to fit the screen
def read_video():
    ret, frame = cap.read()
    rescaled = imutils.resize(frame, width=800) 
    return ret, rescaled

# Set the frame rate for the video.
# For demo purposes, our face will be still
# So, we don't want too may images to be saved
frame_rate = 3 # Set the frame rate for the video. 

prev        = 0 # Temp variable to track time
image_count = 0 # Way to index saved images

# Save images in time stamped directories

if debug == 1 :
   img_dir = Path("images/" + time.strftime("%b_%d_%H_%M"))
   img_dir.mkdir(parents=True, exist_ok=True)
else : 
   img_dir = time.strftime("%b_%d_%H_%M")
        
# I don't have a usb camera. Using a wifi camera in place of usb.
# Using the RTSP feed from wifi camera. 
rtsp = 'rtsp://shajikk:9499032069@192.168.0.7/live'
print("Using Wifi RTSP camera @ ", rtsp)
cap = cv2.VideoCapture(rtsp)

print('Original size of captured frames =', 
        cap.get(cv2.CAP_PROP_FRAME_HEIGHT), "x"  ,  
        cap.get(cv2.CAP_PROP_FRAME_WIDTH)
     )


while(cap.isOpened()):
    _ , frame = read_video()
    time_elapsed = time.time() - prev
    
    if time_elapsed > 1./frame_rate :  
        prev = time.time()  
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        
        for (x, y , w ,h) in faces:
            cv2.rectangle(frame, (x,y), (x+w, y+h), (255, 0 , 0), 3)

            # Cut out face from the frame
            sample_img = frame[y:y+h, x:x+w]

            if debug == 1 :
              name = img_dir/('image_' + str(image_count) + ".png")
              print("Saving Image : ", name)
              cv2.imwrite(str(name), sample_img, params=(cv2.IMWRITE_JPEG_QUALITY, 0))
            else :
              file_name = 'image_' + str(image_count) + ".png"
              _, png = cv2.imencode('.png', sample_img)
              to_send = {'file' : file_name, 'dir' : img_dir, 'data' : png.tobytes()}
              print("Sending Image : ", file_name)
              mqttclient.publish(MQTT_TOPIC, payload=pickle.dumps(to_send), qos=0, retain=False)

            image_count+=1
        
        cv2.imshow('frame', frame)
        
    if cv2.waitKey(1) & 0xFF == ord('q'): break
        
cap.release()
cv2.destroyAllWindows()
if not debug == 1 : mqttclient.loop_stop()
