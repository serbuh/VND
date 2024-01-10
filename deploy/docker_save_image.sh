#!/bin/bash
img_ver=`awk 'NR==1{ print }' docker_version.txt`
cd ..

# Save image to tar
echo Saving image to vnd-$img_ver-image.tar
sleep 1
docker save -o ../vnd-$img_ver-image.tar vnd-$img_ver-image
