#!/usr/bin/env python3

import cv2
import numpy as np
import imutils
import time
from pathlib import Path
import paho.mqtt.client as mqtt
import sys
import pickle
import gc

import tensorflow as tf
import tensorflow.contrib.tensorrt as trt
import os


from tf_trt_models.detection import download_detection_model, build_detection_graph

###### Load the frozen graph

FROZEN_GRAPH_NAME = 'data/frozen_inference_graph_face.pb'
output_dir=''
frozen_graph = tf.GraphDef()
with open(os.path.join(output_dir, FROZEN_GRAPH_NAME), 'rb') as f:
  frozen_graph.ParseFromString(f.read())

#######  A few magical constants

INPUT_NAME='image_tensor'
BOXES_NAME='detection_boxes'
CLASSES_NAME='detection_classes'
SCORES_NAME='detection_scores'
MASKS_NAME='detection_masks'
NUM_DETECTIONS_NAME='num_detections'

input_names = [INPUT_NAME]
output_names = [BOXES_NAME, CLASSES_NAME, SCORES_NAME, NUM_DETECTIONS_NAME]

######## Optimize the frozen graph using TensorRT

trt_graph = trt.create_inference_graph(
    input_graph_def=frozen_graph,
    outputs=output_names,
    max_batch_size=1,
    max_workspace_size_bytes=1 << 25,
    precision_mode='FP16',
    minimum_segment_size=50
)

######### Create session and load graph

tf_config = tf.ConfigProto()
tf_config.gpu_options.allow_growth = True
tf_config.gpu_options.per_process_gpu_memory_fraction = 0.5

tf_sess = tf.Session(config=tf_config)

# use this if you want to try on the optimized TensorRT graph
# Note that this will take a while
# tf.import_graph_def(trt_graph, name='')

# use this if you want to try directly on the frozen TF graph
# this is much faster
tf.import_graph_def(frozen_graph, name='')

tf_input = tf_sess.graph.get_tensor_by_name(input_names[0] + ':0')
tf_scores = tf_sess.graph.get_tensor_by_name('detection_scores:0')
tf_boxes = tf_sess.graph.get_tensor_by_name('detection_boxes:0')
tf_classes = tf_sess.graph.get_tensor_by_name('detection_classes:0')
tf_num_detections = tf_sess.graph.get_tensor_by_name('num_detections:0')



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

# Rescale the the frames to fit the screen
def read_video():
    ret, frame = cap.read()
    #rescaled = imutils.resize(frame, width=800) 
    return ret, frame

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

    frame = imutils.resize(frame, width=300) 

    scores, boxes, classes, num_detections = tf_sess.run([tf_scores, tf_boxes, tf_classes, tf_num_detections], feed_dict={
        tf_input: frame[None, ...]
    })

    boxes = boxes[0] # index by 0 to remove batch dimension
    scores = scores[0]
    classes = classes[0]
    num_detections = num_detections[0]
    
    # suppress boxes that are below the threshold.. 
    DETECTION_THRESHOLD = 0.5
    #print("DEBUG : ", int(num_detections))

    # plot boxes exceeding score threshold
    for i in range(int(num_detections)):
        if scores[i] < DETECTION_THRESHOLD:
            continue 
        # scale box to image coordinates
        box = boxes[i] * np.array([frame.shape[0], frame.shape[1], frame.shape[0], frame.shape[1]])
        x, y , w, h = int(box[1]), int(box[0]), int(box[3] - box[1]), int(box[2] - box[0])
        #print('+++ DEBUG', x, y , w, h)
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
