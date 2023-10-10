# VND - Very Nice Dashboard

Customized implementation of NASA's telemetry visualization tool OpenMCT: https://nasa.github.io/openmct/. 

Telemetry server and some examples are took from https://gitlab.lrz.de/lls/vis-frame

NOTE:   
Don't forget to fetch submodules:
while cloning:
`git clone --recurse-submodules <git url>`
or in already cloned project:
`git submodule update --init --recursive`   

1) To install and start OpenMCT go to `openmct` and:   
`npm install`   
`npm start`
2) To install and start telemetry server go to `Telemetry_Server` and:   
`npm install`   
`npm start`
3) To yield some telemetry from python go to `Telemetry_Server` and:   
`python3 CVAS_artificial_feed.py`