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
status_dict = {"Video FPS"  : (24.3,"Telem",0),
                # "Telem FPS" : (22.0,"Telem",1),
                "frame"     : (23832,"Telem",2),
                # "Last FPC"  : (13,"Status",1),
                "FOV"       : ((60.5, 55.6), "Status", 1),
                "Sensor"    : ("VIS", "Status", 0),
                # "CVS state" : ("Scout", "Status", 1),
                "Counter"   : (-999, "Status", 0),
                "yaw"       : (0.0, "Compass", "#ff0000"),
                "telem_azimuth" : (0.0, "Compass", "#00ff00"),
                "azimuth_out" : (91.0, "Compass", "#0000ff"),
                }


dashboard_channel = ("127.0.0.1", 50020)
dashboard = Dashboard(dashboard_channel)

counter = 0
while True:
    counter += 1
    if counter < 150:
        lst = list(status_dict["Counter"])
        lst[0] = counter
        lst[2] = 1
        status_dict["Counter"] = tuple(lst)
    else:
        lst = list(status_dict["Counter"])
        lst[0] = counter
        status_dict["Counter"] = tuple(lst)
    
    lst = list(status_dict["telem_azimuth"])
    lst[0] = (0.5 * counter) % 360
    status_dict["telem_azimuth"] = tuple(lst)

    lst = list(status_dict["yaw"])
    lst[0] = 360 - status_dict["telem_azimuth"][0] + 60
    status_dict["yaw"] = tuple(lst)

    # Sending dict
    print("Sending {}".format(status_dict))
    dashboard.Send(status_dict)
    time.sleep(1/30.0)