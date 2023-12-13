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

# Define messages interface
### Example of definig message interface for `dashboard_sim_sender.py` 
You need to define a json for openmct (same file is used by telemetry server).   
You can edit the file manually. The file has lots of fields. So there is a simpler way of creating that json.
1) Go to `openmct/messages_interface`
2) Add lines to `fields_in.txt`   
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
1) run `python generate_from_list.py`. Output will be generated in `CVASdictionary.json`

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
