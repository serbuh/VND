from flask import Flask, render_template,Response,request
from flask_socketio import SocketIO,send,emit
import socket
import json
import datetime
import threading
import os
from gevent import monkey

monkey.patch_all()

# Paths
script_folder = os.path.dirname(os.path.abspath(__file__))
openmct_dist = os.path.join(script_folder, "..", "openmct", "dist")


class TelemetryServer():
    def __init__(self):
        self.buf_size = 65535
        self.udp_dashboard_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # self.udp_dashboard_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.udp_dashboard_sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, self.buf_size)
        self.listen = True

        # History DB
        self.historic_data = []
        self.subscribed_keys = {}
        self.historic_data_max_size = 1000

        # Setup Flask server
        self.flask_server = Flask(__name__, static_url_path='', static_folder=openmct_dist, template_folder='templates')
        self.flask_server.config['SECRET_KEY'] = 'secret!'
        self.socketio = SocketIO(self.flask_server, async_mode="gevent")

        self.setup_event_handlers()

    def run_flask(self, browser_port):
        print(f"Running on http://localhost:{browser_port}/index.html")
        self.socketio.run(self.flask_server, debug=False, use_reloader=False, port=browser_port)
    
    def setup_event_handlers(self):
        @self.socketio.on("subscribe")
        def handle_subscribe(key):
            print(f"Subscribe req: {key}")
            self.subscribed_keys[key] = True

        @self.socketio.on("unsubscribe")
        def handle_unsubscribe(key):
            print(f"Unsubscribe req: {key}")
            self.subscribed_keys.pop(key, None)

        @self.flask_server.route('/')
        def static_file():
            return self.flask_server.send_static_file('index.html')

        @self.flask_server.route('/history/<key>/<start>/<end>/<strategy>/<size>')
        def handle_historic_data(key, start, end, strategy, size):
            historic_blob = []
            for msg_batch in self.historic_data:
                if msg_batch["timestamp"] > float(start) and msg_batch["timestamp"] < float(end):
                    for stored_key, value in msg_batch.items(): # Extract the item
                        if stored_key == key: # Find needed key
                            if isinstance(value, list): # Handle tuples in historic. Take only the first value
                                value = value[0]
                            historic_msg = {"id": stored_key, "value": value, "timestamp": msg_batch["timestamp"], "mctLimitState":None}
                            # print(f"One of the historic msgs: {historic_msg}")
                            historic_blob.append(historic_msg)
            print(f"Send {len(historic_blob)} history items for {key}")
            return historic_blob

    def start_data_listening_thread(self, address_listen_to):
        # Start listening for telemetry
        threading.Thread(target=self.start_data_listening, args=(address_listen_to,), daemon=True).start()

    def start_data_listening(self, address_listen_to):
        self.udp_dashboard_sock.bind(address_listen_to)

        print(f"Listening telemetry on {address_listen_to[0]}:{address_listen_to[1]}")

        while self.listen:

            data, _ = self.udp_dashboard_sock.recvfrom(65535) # Blocking. Should be in thread
            timestamp = datetime.datetime.now().timestamp() * 1000

            # New telemetry message
            msg_batch = json.loads(data.decode())
            #print(msg_batch, flush=True)

            # Emit realtime messages to OpenMCT
            with self.flask_server.app_context():
                # Fetch messages that the openmct is subscribed for
                for msg_key, msg_value in msg_batch.items():
                    # Handle spaces (replace with "_")
                    msg_key = msg_key.replace(" ", "_")

                    if self.subscribed_keys.get(msg_key):
                        # Handle tuples in realtime. Take only the first value
                        if isinstance(msg_value, list):
                            msg_value = msg_value[0]
                        self.socketio.emit("realtime", [{"id": msg_key, "value": msg_value, "timestamp":timestamp, "mctLimitState": None}])
            
            # Save history
            msg_batch["timestamp"] = timestamp # append timestamp
            self.historic_data.append(msg_batch) # [{"field_1": 1, "field_2": 2, "timestamp":timestamp}, {...}, ...]
            
            # Cyclic buffer like
            if len(self.historic_data) > self.historic_data_max_size:
                self.historic_data.pop(0)

        

if __name__ == '__main__':
    # Params
    import configparser
    config = configparser.ConfigParser()
    config.read(os.path.join(script_folder, "server_config.ini"))

    browser_port = int(config['Comm']['browser_port'])
    listen_to_ip = config['Comm']['listen_to_ip']
    listen_to_port = int(config['Comm']['listen_to_port'])
    address_listen_to = (listen_to_ip, listen_to_port)

    # Start Telemetry listener
    telemetry_server = TelemetryServer()
    telemetry_server.start_data_listening_thread(address_listen_to)
    telemetry_server.run_flask(browser_port)
    