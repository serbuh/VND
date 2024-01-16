#!/bin/bash

# Use -c flag for CONSOLE MODE

console=false
while [[ $# -ge 1 ]]
do
  key="$1"
  case $key in
    
    -c|console)
        console=true
        shift
        ;;
  esac
  shift
done

if $console; then
  echo "Console mode"
  run_py=generate_telemetry_json.py
else
  echo "GUI mode"
  run_py=interface_creator.py
fi

###############################################################################

# Read version
ver=`awk 'NR==1{ print }' deploy/version.txt`
echo "Version v$ver"
img_ver=`awk 'NR==1{ print }' deploy/docker_version.txt`
echo "Docker version v$img_ver"
container_name=vnd-interface-$img_ver-c

# Remove previous container if exists
docker container rm -f $container_name 2> /dev/null || true

# Allow all users to access X11 Server
xhost +

# Run container
docker run -dt --name $container_name -v$PWD:$PWD -v /tmp/.X11-unix:/tmp/.X11-unix:ro -e DISPLAY=unix$DISPLAY --net=host vnd-$img_ver-image

# Exec running script in container
docker exec -it -w $PWD/interface_creator/python $container_name python3 $run_py

# Wait for killing command
read -p "Press enter to kill container"
docker container rm -f $container_name