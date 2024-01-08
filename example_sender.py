import time
import socket
import json

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
dashboard_channel = ("127.0.0.1", 50020)
dashboard = Dashboard(dashboard_channel)

#Create telemetry dictionary
counter = 0
status_dict = {
    "Status.Counter" : (counter, 0),
    "General.Sinus" : (0, 0),
    "Status.FOV" : ((60.5, 55.6), 0),
    "Status.Sensor" : ("VIS", 0),
    "Compass.yaw" : (0.0, 0),
    "Compass.telem_azimuth" : (0.0, 0),
    "Compass.azimuth_out" : (91.0, 0),
    "This is.undefined value" : (404, 0),
}


# Modify telemetry each iteration of the loop
while True:
    
    status_dict["Status.Counter"] = (counter, 0)
    status_dict["Compass.telem_azimuth"] = ((0.5 * counter) % 360, 0)
    status_dict["Compass.yaw"] = (360 - status_dict["Compass.telem_azimuth"][0], 0)

    # Sending dict
    print("Sending {}".format(status_dict))
    dashboard.Send(status_dict)
    
    time.sleep(1/30.0)
    counter += 1