#!/bin/bash
git config --global --add safe.directory /home/the_sergey/VND/openmct
( cd openmct && npm start ) &
( cd telemetry_server && npm start )
#python3 dashbord_sim_sender.py
