#!/bin/bash

#################################################
# This file should be runned from by the docker #
#################################################

git config --global --add safe.directory $PWD/openmct
( cd openmct && npm start ) &
( cd telemetry_server && npm start )
