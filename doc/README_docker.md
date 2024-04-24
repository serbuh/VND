# Docker

* Docker engine (verify installation: `sudo docker run hello-world`)

# Docker cheetsheet for deploy

Save docker (On deployment machine):   
`docker save -o vnd-docker.tar node:20`

Load docker (On Stand Alone machine):   
`docker load -i vnd-docker.tar`

# Run - linux docker
Run VND + OpenMCT   
`./run_VND.sh`   
[for debug] Run docker in interactive mode   
`./run_VND.sh -i` 