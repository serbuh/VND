import time
import socket
import json

class Dashboard():
    def __init__(self, dashboard_channel):
        self.udp_dashboard_addr = dashboard_channel
        self.udp_dashboard_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_dashboard_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def Send(self, msg):
        msg_serialized = str.encode(json.dumps(msg))
        self.udp_dashboard_sock.sendto(msg_serialized, self.udp_dashboard_addr)


#### test
status_dict = {"Telem.Video FPS"  : (24.3, 0),
                "Telem.Telem FPS" : (22.0, 1),
                "Telem.frame"     : (23832, 2),
                "Status.FOV"       : ((60.5, 55.6), 1),
                "Status.Sensor"    : ("VIS", 0),
                "Status.Counter"   : (-999, 0),
                "Compass.yaw"       : (0.0, "#ff0000"),
                "Compass.telem_azimuth" : (0.0, "#00ff00"),
                "Compass.azimuth_out" : (91.0, "#0000ff"),
                }


dashboard_channel = ("127.0.0.1", 50020)
dashboard = Dashboard(dashboard_channel)

counter = 0
while True:
    counter += 1
    if counter < 150:
        lst = list(status_dict["Status.Counter"])
        lst[0] = counter
        lst[1] = 1 # Color
        status_dict["Status.Counter"] = tuple(lst)
    else:
        lst = list(status_dict["Status.Counter"])
        lst[0] = counter
        lst[1] = 0 # Color
        status_dict["Status.Counter"] = tuple(lst)
    
    lst = list(status_dict["Compass.telem_azimuth"])
    lst[0] = (0.5 * counter) % 360
    status_dict["Compass.telem_azimuth"] = tuple(lst)

    lst = list(status_dict["Compass.yaw"])
    lst[0] = 360 - status_dict["Compass.telem_azimuth"][0] + 60
    status_dict["Compass.yaw"] = tuple(lst)

    # Sending dict
    print("Sending {}".format(status_dict))
    dashboard.Send(status_dict)
    time.sleep(1/30.0)