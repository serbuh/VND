# Remove previous container if exists
docker container rm -f vnd-docker 2> /dev/null || true

# Run container
docker run -dt --name vnd-docker -v$PWD:$PWD --net=host vnd-docker-2024-01-07 

# Exec running script in container
docker exec -it -w $PWD vnd-docker ./apps.sh

# Wait for killing command
read -p "Press enter to kill container"
docker container rm -f vnd-docker


################################################################################
exit 0

# Build image from Dockerfile
docker build -t vnd-docker-2024-01-07 .

# Save image to tar
docker save -o vnd-docker-v1.tar vnd-docker-2024-01-07

or 

docker save vnd-docker-2024-01-07 | gzip > vnd.tgz

# Install image from tar (On target)
docker load -i vnd-docker-v1.tar

or 

gunzip -c vnd.tgz | docker load

