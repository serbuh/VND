#!/bin/bash
img_ver=`awk 'NR==1{ print }' docker_version.txt`
cd ..

# Save image to tar
echo Loading image vnd-$img_ver-image.tar
sleep 1
docker load -i vnd-$img_ver-image.tar
