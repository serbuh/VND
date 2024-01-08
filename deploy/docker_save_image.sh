#!/bin/bash
ver=`awk 'NR==1{ print }' version.txt`
cd ..

# Save image to tar
echo Saveing image to vnd-$ver-image.tar
sleep 1
docker save -o ../vnd-$ver-image.tar vnd-$ver-image
