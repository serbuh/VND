# restart container
docker container rm -f vnd-docker
docker run -dt --name vnd-docker -v$PWD:$PWD --net=host node:20 

docker exec -it -w $PWD vnd-docker ./run.sh

read -p "Press enter to kill container"
docker container rm -f vnd-docker

