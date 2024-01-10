#!/bin/bash

# Read version
ver=`awk 'NR==1{ print }' deploy/version.txt`
echo Running image from: $ver

# Remove previous container if exists
docker container rm -f vnd-$ver-c 2> /dev/null || true

# Allow all users to access X11 Server
xhost +

# Run container
docker run -dt --name vnd-$ver-c -v$PWD:$PWD -v /tmp/.X11-unix:/tmp/.X11-unix:ro -e DISPLAY=unix$DISPLAY --net=host vnd-$ver-image

# Exec running script in container
docker exec -it -w $PWD vnd-$ver-c ./apps.sh

# Wait for killing command
read -p "Press enter to kill container"
docker container rm -f vnd-$ver-c


exit 0
################################################################################

# Build image from Dockerfile
docker build -t vnd-$ver-image . -f node.Dockerfile

# Run container from image
docker run -dt --name vnd-$ver-c -v$PWD:$PWD --net=host vnd-$ver-image

# Exec docker
docker exec -it -w $PWD vnd-$ver-c bash

# Save image to tar
docker save -o vnd-$ver-image.tar vnd-$ver-image
or 
docker save vnd-$ver-image | gzip > vnd-$ver-image.tgz

# Install image from tar (On target)
docker load -i vnd-$ver-image.tar
or 
gunzip -c vnd-$ver-image.tgz | docker load

#kill all running containers
docker kill $(docker ps -q)

#delete all stopped containers
docker rm $(docker ps -a -q)

