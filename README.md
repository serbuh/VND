# VND - Very Nice Dashboard

Web based customized implementation of NASA's telemetry visualization tool    
OpenMCT official git: https://nasa.github.io/openmct/

Tested with:   
`node v18.18.0, v18.18.2, v20.6.1`   
`npm v9.8.1, v10.1.0`   

# Install

* Updated browser!
* Install Node.js: https://nodejs.org/en/download
* Install python
* Create virtualenv with name `env` : `install_requirements.<sh/bat>`

# Defining interface and ports
Use GUI: `run_interface_creator.<bat/sh>`   
* GUI edits openmct json   
`openmct/telemetry_plugin/openmct_interface.json`   
You can do it manually if you know what you are doing

# Online installation
To install modules from internet:
```
cd openmct && npm install
```

To create new deployment version (DEV):
```
npm run build:dev
```
NOTE: In `openmct/.webpack/webpack.dev.js` change   
`__OPENMCT_ROOT_RELATIVE__: '"dist/"'`   
to   
`__OPENMCT_ROOT_RELATIVE__: '""'`

To create new deployment version (Production):
```
npm run build:prod
```


# Run
```
run_VND.<sh/bat>
```
Manually:
```
cd openmct && npm start
```

# Telemetry producer example
```
cd emulator
python data_sender.py
```

# Open OpenMCT in a browser
```
localhost:8080
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
