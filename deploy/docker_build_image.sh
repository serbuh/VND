#!/bin/bash
ver=`awk 'NR==1{ print }' version.txt`
cd ..

echo Build vnd-$ver-image
sleep 1
# Build image from Dockerfile
docker build -t vnd-$ver-image . -f node.Dockerfile
