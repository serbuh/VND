import socket
import json

class Socket():
    def __init__(self, channel, big_buffer=False, reuse_addr=False):
        self.udp_dashboard_addr = channel
        self.udp_dashboard_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        if big_buffer:
            self.udp_dashboard_sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF,2**23)
        if reuse_addr:
            self.udp_dashboard_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def send_serialized(self, msg_serialized):
        self.udp_dashboard_sock.sendto(msg_serialized, self.udp_dashboard_addr)
    
    def send_json(self, msg):
        msg_serialized = str.encode(json.dumps(msg))
        self.udp_dashboard_sock.sendto(msg_serialized, self.udp_dashboard_addr)