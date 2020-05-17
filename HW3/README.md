# Internet of Things

- List of files

 - Dockerfile.l4t-base
   Docker file for CUDA ubundu for tx2.

 - face_detect.py
   Main program that runs by default after cuda_base container (Dockerfile.l4t-base above) boots up.

 - clean_images
   Used for cleaning the local image directory when face_detect.py is run in debug mode.

 - mosquitto_pub_test.py
   This is used for initial testing of pipeline. Instead of sending images, it sends text files. Used for initial pipe cleaning of the pipeline. 

 - Dockerfile.common.broker
   Docker file for broker. This just runs the mosquitto service.

 - Dockerfile.tx2.forward
   Docker file for MQTT traffic forwarder to IBM cloud.

 - tx2_forward.py
   Main program that runs by default after tx2_forward container (Dockerfile.tx2.forward above) boots up.

 - Dockerfile.cloud.saver
   Docker file for containter that gets data from cloud broker and saves in IBM S3 object storage

 - entrypoint.sh
   This serves as an entry point for the docker container Dockerfile.cloud.saver. It mounts S3 object storage using s3fs and proceed to run the main microservice.

 - cloud_saver.py
   Main program that runs by default after cloud_saver container ( Dockerfile.cloud.saver above) boots up.


docker network rm tx2
docker rm $(docker ps -a -q)

docker network rm cloud
docker rm $(docker ps -a -q)

eg. Login : docker exec -it tx2_broker  /bin/sh

*) sudo docker network create --driver bridge tx2
   sudo docker network inspect tx2 [inspect bridge]

1) sudo docker build -t l4t-base.1 -f Dockerfile.l4t-base .
   sudo docker run -it --rm --name=cuda_base --network=tx2 --hostname="l4t_base" --volume $PWD:/home/work  --runtime nvidia  -e DISPLAY=$DISPLAY -v /tmp/.X11-unix/:/tmp/.X11-unix  l4t-base.1:latest

2) sudo docker build -t common.broker.1 -f Dockerfile.common.broker .
   sudo docker run -it --rm  --name="tx2_broker" --network=tx2 --hostname="tx2_broker"  --volume $PWD:/home/work -p 1883:1883  common.broker.1:latest

3) sudo docker build -t tx2.forward.1 -f Dockerfile.tx2.forward .
   # Get it from ENV : to do
   sudo docker run -it --rm  --name=tx2_forward --twork=tx2 --hostname="tx2_forward" --volume $PWD:/home/work -e REMOTE_HOST='169.45.121.163' tx2.forward.1:latest


*) sudo docker network create --driver bridge cloud
   sudo docker network inspect cloud


4) sudo docker build -t common.broker.1 -f Dockerfile.common.broker .
   docker run -it --rm  --name="cloud_broker" --network=cloud --hostname="cloud_broker"  --volume $PWD:/home/work -p 1883:1883  common.broker.1:latest

5) sudo docker build -t cloud.saver.1 -f Dockerfile.cloud.saver .
   docker run -it --rm  --privileged  --name="cloud_saver" --network=cloud --hostname="cloud_saver" --volume $PWD:/home/work    cloud.saver.1:latest

Test : ./mosquitto_pub_test.py

Check : 

ssh root@169.45.121.163
sudo docker exec -it cloud_saver /bin/bash
df -h
cd /mnt/drive0
