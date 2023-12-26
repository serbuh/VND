echo Killing previous instances
call kill_all.bat

start CMD /k "TITLE TelemetryServer && cd telemetry_server && npm start"
start CMD /k "TITLE OpenMCT && cd openmct && npm start"