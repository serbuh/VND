#!/bin/bash

# Read version
ver=`awk 'NR==1{ print }' deploy/version.txt`
echo Running image from: $ver
container_name=vnd-interface-$ver-c

# Remove previous container if exists
docker container rm -f $container_name 2> /dev/null || true

# Allow all users to access X11 Server
xhost +

# Run container
docker run -dt --name $container_name -v$PWD:$PWD -v /tmp/.X11-unix:/tmp/.X11-unix:ro -e DISPLAY=unix$DISPLAY --net=host vnd-$ver-image

# Exec running script in container
docker exec -it -w $PWD/interface_creator/python $container_name python3 generate_from_list.py

# Wait for killing command
read -p "Press enter to kill container"
docker container rm -f $container_name