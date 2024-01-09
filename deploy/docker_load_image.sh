#!/bin/bash
ver=`awk 'NR==1{ print }' version.txt`
cd ..

# Save image to tar
echo Loading image vnd-$ver-image.tar
sleep 1
docker load -i vnd-$ver-image.tar
