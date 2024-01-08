# Remove previous container if exists
ver=2024-01-08
echo Running image from: $ver
docker container rm -f vnd-$ver-c 2> /dev/null || true

# Run container
docker run -dt --name vnd-$ver-c -v$PWD:$PWD --net=host vnd-$ver-image

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
docker exec -it vnd /bin/bash

# Save image to tar
docker save -o vnd-$ver-image.tar vnd-$ver-image
or 
docker save vnd-$ver-image | gzip > vnd-$ver-image.tgz

# Install image from tar (On target)
docker load -i vnd-$ver-image.tar
or 
gunzip -c vnd-$ver-image.tgz | docker load

