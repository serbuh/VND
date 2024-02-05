#!/bin/bash

# Use -i flag for INTERACTIVE DOCKER MODE

interactive=false
while [[ $# -ge 1 ]]
do
  key="$1"
  case $key in
    
    -i|interactive)
        interactive=true
        shift
        ;;
  esac
  shift
done

if $interactive; then
  echo "Interactive mode"
  cmd=bash
else
  cmd=./apps.sh
fi

###############################################################################

# Read version
ver=`awk 'NR==1{ print }' deploy/version.txt`
echo "Version v$ver"
img_ver=`awk 'NR==1{ print }' deploy/docker_version.txt`
echo "Docker version v$img_ver"
container_name=vnd-$img_ver-c

# Remove previous container if exists
docker container rm -f $container_name 2> /dev/null || true

# Allow all users to access X11 Server
xhost +

# Run container
docker run -dt --name $container_name -v$PWD:$PWD -v /tmp/.X11-unix:/tmp/.X11-unix:ro -e DISPLAY=unix$DISPLAY --net=host vnd-$img_ver-image

# Exec running script in container
docker exec -it -w $PWD $container_name $cmd

# Wait for killing command
read -p "Press enter to kill container"
docker container rm -f $container_name


exit 0
################################################################################

# Build image from Dockerfile
docker build -t vnd-$img_ver-image . -f node.Dockerfile

# Run container from image
docker run -dt --name vnd-$img_ver-c -v$PWD:$PWD --net=host vnd-$img_ver-image

# Exec docker
docker exec -it -w $PWD vnd-$img_ver-c bash

# Save image to tar
docker save -o vnd-$img_ver-image.tar vnd-$img_ver-image
or 
docker save vnd-$img_ver-image | gzip > vnd-$img_ver-image.tgz

# Install image from tar (On target)
docker load -i vnd-$img_ver-image.tar
or 
gunzip -c vnd-$img_ver-image.tgz | docker load

#kill all running containers
docker kill $(docker ps -q)

#delete all stopped containers
docker rm $(docker ps -a -q)

