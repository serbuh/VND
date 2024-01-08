#!/bin/bash

git config --global --add safe.directory $PWD/openmct
( cd openmct && npm start ) &
( cd telemetry_server && npm start )
#python3 example_sender.py
