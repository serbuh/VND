#!/bin/bash
img_ver=`awk 'NR==1{ print }' docker_version.txt`
cd ..

echo Build vnd-$img_ver-image
sleep 1
# Build image from Dockerfile
docker build -t vnd-$img_ver-image . -f node.Dockerfile
