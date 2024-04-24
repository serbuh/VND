# "Simple interface format" spec
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