import time
import socket
import json
import math
import random

# UDP connection class
class Dashboard():
    def __init__(self, dashboard_channel):
        self.udp_dashboard_addr = dashboard_channel
        self.udp_dashboard_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_dashboard_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def Send(self, msg):
        msg_serialized = str.encode(json.dumps(msg))
        self.udp_dashboard_sock.sendto(msg_serialized, self.udp_dashboard_addr)

# Create udp connection
dashboard_channel = ("127.0.0.1", 5555)
print(f"Sending to {dashboard_channel[0]}:{dashboard_channel[1]}")
dashboard = Dashboard(dashboard_channel)

#Create telemetry dictionary
counter = 0
status_dict = {
    "Status.Counter" : counter,
    "Status.State" : "GOOD",
    "Status.StateEnum" : 1,
    "Telem.vector" : str((60.5, 55.6)),
    "Telem.Sinus" : 0,
    "Telem.Sinus_noisy" : 0,
    "Telem.Sinus_drifting" : 0,
    "Location.lat": 0,
    "Location.lon": 0,
    "Location.alt": 0,
    "Compass.azimuth" : 0.0,
    "Compass.azimuth2" : 0.0,
    "This_is.undefined_value" : 404,
}

# Modify telemetry each iteration of the loop
combined_noise = 0
while True:
    # Play with values
    state = int( counter / 100 ) % 3
    if state == 0:
        status = "BAD"
        status_enum = 0
    elif state == 1:
        status = "NORMAL"
        status_enum = 1
    else:
        status = "GOOD"
        status_enum = 2
    
    
    azimuth = (0.5 * counter) % 360
    sinus = math.sin(math.radians(counter/2))
    
    noise = (0.5-random.random())/5
    sinus_noisy = sinus + noise

    combined_noise += noise
    sinus_drifting = sinus + combined_noise

    # Update dictionary
    status_dict["Status.Counter"]       = counter
    status_dict["Status.State"]         = status
    status_dict["Status.StateEnum"]     = status_enum
    status_dict["Telem.Sinus"]          = sinus
    status_dict["Telem.Sinus_noisy"]    = sinus_noisy
    status_dict["Telem.Sinus_drifting"] = sinus_drifting
    status_dict["Location.lat"]         = 31.0
    status_dict["Location.lon"]         = 31.0
    status_dict["Location.alt"]         = 31.0
    status_dict["Compass.Magnitometer.A.azimuth"]  = azimuth
    status_dict["Compass.Magnitometer.B.azimuth2"] = 360 - azimuth

    # Sending dict
    # print(f"Sending {status_dict}\r")
    print(f"Sending {counter}", end="\r")
    dashboard.Send(status_dict)
    
    time.sleep(1/30.0)
    counter += 1