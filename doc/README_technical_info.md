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
          from: 'telemetry_plugin',
          to: 'telemetry_plugin'
        },
    ...
```
In `openmct/index.html` added lines:
```
    openmct.install(openmct.plugins.TelemetryDictionaryPlugin());
    openmct.install(openmct.plugins.HistoricalTelemetryPlugin('TelemetryDomainObject', '/CVASHistory/', 'localhost'));
    openmct.install(openmct.plugins.RealtimeTelemetryPlugin('TelemetryDomainObject', '/CVASRealtime/', 'localhost'));
```

In `openmct/src/plugins/plugins.js` added lines:
```
import HistoricalTelemetryPlugin from '../../telemetry_plugin/historical-telemetry-plugin.js';
import RealtimeTelemetryPlugin from '../../telemetry_plugin/realtime-telemetry-plugin.js';
import TelemetryDictionaryPlugin from '../../telemetry_plugin/telemetry-dictionary-plugin.js';

...

plugins.HistoricalTelemetryPlugin = HistoricalTelemetryPlugin;
plugins.RealtimeTelemetryPlugin = RealtimeTelemetryPlugin;
plugins.TelemetryDictionaryPlugin = TelemetryDictionaryPlugin;
```