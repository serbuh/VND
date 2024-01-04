# VND - Very Nice Dashboard

Web based customized implementation of NASA's telemetry visualization tool OpenMCT: https://nasa.github.io/openmct/

Don't forget to fetch submodules   
while cloning:   
`git clone --recurse-submodules <git url>`   
or if already in cloned project:   
`git submodule update --init --recursive`   
If sumbodule is somehow not accessable due to permissions issues - try downloading it manually.   

# Installs, Prerequisites
Tested with:   
`node v18.18.0, v18.18.2, v20.6.1`   
`npm v9.8.1, v10.1.0`   

* Donload Node.js   
Download page: https://nodejs.org/en/download   
[for Ubuntu] download e.g.   
https://nodejs.org/dist/v20.10.0/node-v20.10.0-linux-x64.tar.xz
```
sudo tar -xvf node-v20.10.0-linux-x64.tar.xz
sudo ln -f -s <path to extracted node>/node-v20.10.0-linux-x64/bin/node /usr/local/bin/node
```
* Updated browser   
  (Sometimes there are issues with the older versions)
* Install node modules   
  (See below)   

Install node modules for Telemetry Server
```
cd VND/telemetry_server
npm install
```
Install node modules for OpenMCT
```
cd VND/openmct
npm install
```

# Define messages interface
Use interface_creator tool. The tool takes simple format (look at `interface_creator/python/examples/...`) and turns it into OpenMCT json format (`CVASDictionary.json`)   

Python version that uses (requires pip package PySimpleGUI):   
`run_interface_creator_py.bat`   

Or exe version:   
`run_interface_creator_exe.bat`   

Simple format means:
* each field means one message type
* default message type is float (described as 'integer' in json. Have no idea why)
* If you want to send a string, not a float - use 'S:' prefix. That will tell the script to put a 'string' type in json
```
Telem.Video FPS
Telem.Telem FPS
Telem.frame
Status.FOV
S:Status.Sensor
Status.Counter
Compass.yaw
Compass.telem_azimuth
Compass.azimuth_out
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
Added historical and realtime telemetry plugins (`telemetry_plugin` folder)   
Added messages interface (`messages_interface` folder)   

In `openmct/.webpack/webpack.common.js` added lines:
```
const config = {
    new VueLoaderPlugin(),
    new CopyWebpackPlugin({
      patterns: [
        {
          from: 'messages_interface/CVASdictionary.json',
          to: 'messages_interface/CVASdictionary.json'
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
