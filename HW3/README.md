# Internet of Things

## List of files  

 - Dockerfile.l4t-base:  
   Docker file for CUDA ubundu for tx2.

 - face_detect.py:  
   Main program that runs by default after cuda_base container (Dockerfile.l4t-base above) boots up.

 - clean_images:  
   Used for cleaning the local image directory when face_detect.py is run in debug mode.

 - mosquitto_pub_test.py: 
   This is used for initial testing of pipeline. Instead of sending images, it sends text files. Used for initial pipe cleaning of the pipeline. 

 - Dockerfile.common.broker:  
   Docker file for broker. This just runs the mosquitto service.

 - Dockerfile.tx2.forward:  
   Docker file for MQTT traffic forwarder to IBM cloud.

 - tx2_forward.py:  
   Main program that runs by default after tx2_forward container (Dockerfile.tx2.forward above) boots up.

 - Dockerfile.cloud.saver:  
   Docker file for containter that gets data from cloud broker and saves in IBM S3 object storage

 - entrypoint.sh:  
   This serves as an entry point for the docker container Dockerfile.cloud.saver. It mounts S3 object storage using s3fs and proceed to run the main microservice.

 - cloud_saver.py:  
   Main program that runs by default after cloud_saver container ( Dockerfile.cloud.saver above) boots up.

 - .cos_creds:  
   Needed for s3 mounting to work. Excluded from git due to security. 

## Setup and workflow.

Clone this repo into jetson tx2. Populate the ".cos_creds" with s3 access credentials. Start an VM in the cloud. Copy over (or clone) this HW directory into the VM.
For example, Rsync can be used for copying the HW3 into the remote VM 

```bash
rsync -avz -e "ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null"    \
--progress  /data/w251/DL_edge/HW3  root@xxx.xxx.xx.xx:/root/w251/
```

## Initial clean up

First, remove any networks and stopped containers.

In Jetson TX2 do :

```bash
docker network rm tx2
docker rm $(docker ps -a -q)
```

In VM in the cloud :
```bash
docker network rm cloud
docker rm $(docker ps -a -q)
```

## Steps

### Create a bridge network at Tx2 (Jetson side)

```bash
# Create tx2 bridge
sudo docker network create --driver bridge tx2

# Inspect the network.
sudo docker network inspect tx2 [inspect bridge]
```

### Build & Boot up cuda ubundu, connect it to tx2 bridge network (Jetson)

```bash
# Build the docker image
sudo docker build -t l4t-base.1 -f Dockerfile.l4t-base .

# Export the display explicitly. The default display "jetson:1.0" is not working
# Probably because Xfce is made the display manager, instead of Unity. 
export DISPLAY=192.168.0.191:1.0

# Run the container. 
sudo docker run -it --rm --name=cuda_base --network=tx2 --hostname="l4t_base" \
--volume $PWD:/home/work  --runtime nvidia  -e DISPLAY=$DISPLAY \
-v /tmp/.X11-unix/:/tmp/.X11-unix  l4t-base.1:latest
```

- Note that the Container polls for tx2 MQTT broker to be up before proceeding with frame capture.  
- RTSP wifi camera is used instead of USB camera, as I don't have a USB camera.   
- The the default frame size of the Wifi camera is 1080p. This is rescaled to a lower resolution for fitting the camera feed on to the Ubundu Xfce desktop.   
- The frame rate is also adjusted (currently 3fps) for this demo.  
- Face is captured by OpenCV. The name of the file and the directory where the captured image file needs to be stored is set in this conatiner itself. All the information is pickled into a binary stream and send to the endpoint.  
- `mosquitto_pub_test.py`  can be used to test the pipeline.  
- Probably bring up as the last piece in pipeline, else when the container boots up it immiediately starts sending the package. 

### Bring up the MQTT broker in jetson,  connect it to tx2 bridge network (Jetson)

```bash
# Build the docker image
sudo docker build -t common.broker.1 -f Dockerfile.common.broker .

# mosquitto -v is the only process running in the broker.
sudo docker run -it --rm  --name="tx2_broker" --network=tx2 \
--hostname="tx2_broker"  --volume $PWD:/home/work -p 1883:1883  \
common.broker.1:latest
```

### Bring up the Package forwarder in jetson,  connect it to tx2 bridge network (Jetson)
```bash
# Build the docker image
sudo docker build -t tx2.forward.1 -f Dockerfile.tx2.forward .

# Executes tx2_forward.py as a micro service.
sudo docker run -it --rm  --name=tx2_forward --twork=tx2 \
--hostname="tx2_forward" --volume $PWD:/home/work \
-e REMOTE_HOST='169.45.121.163' tx2.forward.1:latest
```
- `REMOTE_HOST` needs to be provided as the env variable. This will be used by `tx2_forward.py`. The ip address is the ip address of the remote VM in the cloud.


*) sudo docker network create --driver bridge cloud
   sudo docker network inspect cloud


4) sudo docker build -t common.broker.1 -f Dockerfile.common.broker .
   docker run -it --rm  --name="cloud_broker" --network=cloud --hostname="cloud_broker"  --volume $PWD:/home/work -p 1883:1883  common.broker.1:latest

5) sudo docker build -t cloud.saver.1 -f Dockerfile.cloud.saver .
   docker run -it --rm  --privileged  --name="cloud_saver" --network=cloud --hostname="cloud_saver" --volume $PWD:/home/work    cloud.saver.1:latest

eg. Login : docker exec -it tx2_broker  /bin/sh
Test : ./mosquitto_pub_test.py

Check : 

ssh root@169.45.121.163
sudo docker exec -it cloud_saver /bin/bash
df -h
cd /mnt/drive0
