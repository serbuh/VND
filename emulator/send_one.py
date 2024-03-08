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

# Send
status_dict = {"Status.State" : "GOOD"}
dashboard.Send(status_dict)
print(f"Sent {status_dict}")