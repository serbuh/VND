# VND - Very Nice Dashboard

Customized implementation of NASA's telemetry visualization tool OpenMCT: https://nasa.github.io/openmct/

NOTE:   
Don't forget to fetch submodules   
while cloning:   
`git clone --recurse-submodules <git url>`   
or if already in cloned project:   
`git submodule update --init --recursive`   

# Install node modules before start
TelemetryServer
```
cd TelemetryServer
npm install
```
OpenMCT
```
cd openmct
npm install
```

# Start VND
Start TelemetryServer
```
cd TelemetryServer
npm start
```
Start OpenMCT
```
cd openmct
npm start
```
# Telemetry example
To send some telemetry to VND start:
```
python dashboard_sim_sender.py
```