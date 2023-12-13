# VND - Very Nice Dashboard

Customized implementation of NASA's telemetry visualization tool OpenMCT: https://nasa.github.io/openmct/

NOTE:   
Don't forget to fetch submodules   
while cloning:   
`git clone --recurse-submodules <git url>`   
or if already in cloned project:   
`git submodule update --init --recursive`   

Tested with:   
`node v18.18.0`   
`npm v10.1.0`   

# Install node modules before start
Telemetry Server
```
cd VND/telemetry_server
npm install
```
OpenMCT
```
cd VND/openmct
npm install
```

# Start VND
Start Telemetry Server
```
cd VND/telemetry_server
npm start
```
Start OpenMCT
```
cd VND/openmct
npm start
```
Open OpenMCT webpage in a browser
```
localhost:8080
```
# Telemetry example
To send some telemetry to VND start:
```
python dashboard_sim_sender.py
```

# Technical info
Changes that have been made to raw openMCT version:


# Links
| | |
|-|-|
| About OpenMCT | https://nasa.github.io/openmct/about-open-mct/ |
| Github | https://github.com/nasa/openmct |
| Telemetry Adapter Tutorial | https://github.com/nasa/openmct-tutorial |
| User Guide (GUI) | https://nasa.github.io/openmct/static/files/Open_MCT_Users_Guide.pdf |
| Big readme (API) | https://github.com/nasa/openmct/blob/master/API.md |
| Youtube guide for the telemetry server (JS) (by TUM student) | https://www.youtube.com/playlist?list=PLWAvG5LVeBRVgN-MH8NbRGIRosDzcge3h
| Git for Youtube guide | https://gitlab.lrz.de/lls/vis-frame |
| Nice presentation of the OpenMCT | https://arc.aiaa.org/doi/pdf/10.2514/6.2018-2508 |
| Some plugins | https://nasa.github.io/openmct/plugins/ |
