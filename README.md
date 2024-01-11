# VND - Very Nice Dashboard

Web based customized implementation of NASA's telemetry visualization tool    
OpenMCT official git: https://nasa.github.io/openmct/

NOTE:   
Don't forget to get openmct as a submodule.   
If sumbodule is somehow not accessable due to permissions issues - try downloading it manually into `openmct` folder   

Fetch submodules while cloning:   
`git clone --recurse-submodules <git url>`   
Fetch submodules for already cloned project:   
`git submodule update --init --recursive`   

Tested with:   
`node v18.18.0, v18.18.2, v20.6.1`   
`npm v9.8.1, v10.1.0`   

# Install - Windows
Prerequisites:
* Updated browser!
* Node.js (https://nodejs.org/en/download)
* [optional] python with PySimpleGUI package

# Install - linux
Prerequisites:
* Updated browser!
* Docker engine (verify installation: `sudo docker run hello-world`)

### Following installations are not needed if you are using docker
* Node.js
* python with PySimpleGUI package

### Node.js manual installatiobn
1) Dowload https://nodejs.org/dist/v20.10.0/node-v20.10.0-linux-x64.tar.xz
2) Extract node to some folder   
`sudo tar -xvf node-v20.10.0-linux-x64.tar.xz`
3) Link to that node version   
`sudo ln -f -s <path to extracted node>/node-v20.10.0-linux-x64/bin/node /usr/local/bin/node`


### Install node modules
Requires internet connection.   
OR   
If you got distributed version of VND for StandAlone machines - this step is already done for you.   

To install modules from internet:
```
cd telemetry_server && npm install
cd ..
cd openmct && npm install
```

# Define messages interface and port
Use "simple interface format" (`interface_creator/python/examples/...`) and generate OpenMCT json format from it.
Your options:   
1) [Recommended] Use python GUI tool   
[linux docker] `./run_interface_creator.sh`   
[windows] `runners/windows/run_interface_creator_py.bat`   
[windows] `runners/windows/run_interface_creator_exe.bat`   
[manual] `cd interface_creator/python && python interface_creator.py`   

1) Use python console tool   
[linux docker] `./run_interface_creator.sh -c`   
[manual] `cd interface_creator/python && python generate_from_list.py`

1) Edit openmct json   
`openmct/messages_interface/openmct_interface.json`   
NOTE: Not recomended to do it manually. This approach is recommended if you have your own interface tool that converts your interface to openmct json.


### "Simple interface format" spec
* each field means one message type
* default message type is float (described as 'integer' in json. Have no idea why)
* If you want to send a string, not a float - use 'S:' prefix. That will tell the script to put a 'string' type in json
```
SomeSection.Some field name
status.the_status
location.lat
location.lon
location.alt
S:Status.State
compass.azimuth
```

# Run - windows
Run OpenMCT   
`runners/windows/run_openmct.bat`   
Run VND   
`runners/windows/run_telemetry_server.bat`

# Run - linux docker
Run VND + OpenMCT   
`./run_VND.sh`   
[for debug] Run docker in interactive mode   
`./run_VND.sh -i` 

# Run - manually
Run OpenMCT
```
cd openmct && npm start
```
Start Telemetry Server   
(for the first time you need to wait untill openMCT finishes the build for the `distr` folder)
```
cd telemetry_server && npm start
```
# Open OpenMCT in a browser
```
localhost:8080
```

# Telemetry sender example
To send some telemetry to VND start:
```
[linux] python dashboard_sim_sender.py
```

# Docker cheetsheet for deploy

Save docker (On deployment machine):   
`docker save -o vnd-docker.tar node:20`

Load docker (On Stand Alone machine):   
`docker load -i vnd-docker.tar`

# Technical info
Changes that have been made to raw openMCT version:   
Added historical and realtime telemetry plugins (`telemetry_plugin` folder)   
Added messages interface (`messages_interface` folder)   

In `openmct/.webpack/webpack.common.js` added lines:
```
const config = {
    new VueLoaderPlugin(),
    new CopyWebpackPlugin({
      patterns: [
        {
          from: 'messages_interface/openmct_interface.json',
          to: 'messages_interface/openmct_interface.json'
        },
        {
          from: 'telemetry_plugin',
          to: 'telemetry_plugin'
        },
    ...
```
In `openmct/index.html` added lines:
```
    openmct.install(openmct.plugins.CVASPlugin());
    openmct.install(openmct.plugins.HistoricalTelemetryPlugin('CVAS.telemetry', '/CVASHistory/', 'localhost'));
    openmct.install(openmct.plugins.RealtimeTelemetryPlugin('CVAS.telemetry', '/CVASRealtime/', 'localhost'));
```

In `openmct/src/plugins/plugins.js` added lines:
```
define([
  ...
  '../../telemetry_plugin/historical-telemetry-plugin',
  '../../telemetry_plugin/realtime-telemetry-plugin',
  '../../telemetry_plugin/CVAS-plugin'
  ], function (
  ...
  HistoricalTelemetryPlugin,
  RealtimeTelemetryPlugin,
  CVASPlugin
) {
  const plugins = {};
  ...
  plugins.HistoricalTelemetryPlugin = HistoricalTelemetryPlugin;
  plugins.RealtimeTelemetryPlugin = RealtimeTelemetryPlugin;
  plugins.CVASPlugin = CVASPlugin;

  return plugins;
});
```

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

FAQ / Known Problems
--------
[Q] History telemetry fails to load with error: ```Error fetching data TypeError: Object.hasOwn is not a function```   
[A] Update your browser. Or as written in the issue https://github.com/nasa/openmct/issues/4863 :   
Change all the lines that look like:   
```Object.hasOwn(requestProvider, 'request')```   
to   
```Object.prototype.hasOwnProperty.call(requestProvider, 'request')```
