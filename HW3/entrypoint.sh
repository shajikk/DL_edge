#!/bin/sh
echo "*******Executing s3fs mount *******"
s3fs  cos1-cos-standard-skk1 /mnt/drive0 -o passwd_file=/home/work/.cos_creds -o sigv2 -o use_path_request_style -o url=http://s3.us-east.cloud-object-storage.appdomain.cloud
df -h
exec "$@"
