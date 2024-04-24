from flask import Flask
from flask_socketio import SocketIO
from telemetry_server.config_parser import TelemServerConfig
import socket
import json
import datetime
import threading
import os
from gevent import monkey
import json
import base64
import pickle

monkey.patch_all()

# Paths
script_folder = os.path.dirname(os.path.abspath(__file__))
openmct_dist = os.path.join(script_folder, "..", "openmct", "dist")
openmct_interface_json_path = os.path.join(openmct_dist, "telemetry_plugin", "openmct_interface.json")


class TelemetryServer():
    def __init__(self):
        self.buf_size = 65535
        
        # Data
        self.udp_dashboard_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_dashboard_sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, self.buf_size)
        
        # Video
        self.udp_video_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_video_sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, self.buf_size)
        self.listen = True

        # History DB
        self.historic_data = []
        self.subscribed_keys = {}
        self.historic_data_max_size = 10000
        self.predefined_keys = self.read_predefined_interface(openmct_interface_json_path)
        self.received_keys = []

        # Setup Flask server
        self.flask_server = Flask(__name__, static_url_path='', static_folder=openmct_dist, template_folder='templates')
        self.flask_server.config['SECRET_KEY'] = 'secret!'
        self.socketio = SocketIO(self.flask_server, async_mode="gevent")

        self.setup_event_handlers()
        
    
    def read_predefined_interface(self, interface_json_path):
        if not os.path.exists(interface_json_path):
            print(f"ERROR: OpenMCT predefined interface json does not exist:\n{interface_json_path}")
            exit()
        
        # Load JSON data from file
        with open(interface_json_path, 'r') as json_file:
            parsed_interface = json.load(json_file)
        
        predefined_keys = [measurement["key"] for measurement in parsed_interface["measurements"]]
        #print(predefined_keys)

        print(f"Interface entries: {len(predefined_keys)}. Ver: {parsed_interface.get('version', None)}")
        
        return predefined_keys

    def run_flask(self, browser_port):
        print(f"Running on http://localhost:{browser_port}")
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

    def start_video_listening_thread(self, address_listen_to):
        # Start listening for telemetry
        threading.Thread(target=self.start_video_listening, args=(address_listen_to,), daemon=True).start()

    def start_video_listening(self, address_listen_to):
        self.udp_video_sock.bind(address_listen_to)

        print(f"Listening video on {address_listen_to[0]}:{address_listen_to[1]}")
        frames_count = 0
        while self.listen:

            data, _ = self.udp_video_sock.recvfrom(self.buf_size) # Blocking. Should be in thread
            timestamp = datetime.datetime.now().timestamp() * 1000

            # Emit realtime video to OpenMCT
            with self.flask_server.app_context():
                self.socketio.emit("live-video", {"timestamp": timestamp, "frames_count": frames_count, "data": base64.b64encode(data).decode()})
            
            # NOTE History of frames has not yet implemented
                
            frames_count += 1

    def start_data_listening(self, address_listen_to):
        self.udp_dashboard_sock.bind(address_listen_to)

        print(f"Listening telemetry on {address_listen_to[0]}:{address_listen_to[1]}")

        while self.listen:

            data, _ = self.udp_dashboard_sock.recvfrom(self.buf_size) # Blocking. Should be in thread
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

                    # Check if the key is never received earlier
                    if not msg_key in self.received_keys:
                        if msg_key in self.predefined_keys:
                            print(f"New: {msg_key}")
                        else:
                            print(f"Undefined: {msg_key}")
                        self.received_keys.append(msg_key)

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
            
            # Dump historic data to file
            if False:
                self.save_historic_data()
    
    def save_historic_data(self):
        if not len(self.historic_data):
            return
        
        start_millisec = self.historic_data[0]['timestamp']
        stop_millisec = self.historic_data[-1]['timestamp']
        f_year, f_month, f_day, f_hour, f_minute, f_sec = self.convert_millisec_to_date_string(start_millisec)
        duration_minutes = round((stop_millisec - start_millisec) / 1000 / 60, 1)
        
        # Dump history to file
        dump_file = f"dump_{f_year}-{f_month}-{f_day}__{f_hour}-{f_minute}-{f_sec}__{duration_minutes}_min.pkl"
        with open(dump_file, 'wb') as f:
            pickle.dump(self.historic_data, f)
            
    def convert_millisec_to_date_string(self, timestamp_milliseconds):
        # Convert milliseconds since epoch to a datetime object
        timestamp_seconds = timestamp_milliseconds / 1000  # Convert milliseconds to seconds
        t = datetime.datetime.fromtimestamp(timestamp_seconds)

        # Extract year, month, and day from the datetime object
        return t.year, t.month, t.day, t.hour, t.minute ,t.second
        

if __name__ == '__main__':
    cfg = TelemServerConfig(os.path.join(script_folder, "server_config.ini"))
    
    # Start Telemetry listener
    telemetry_server = TelemetryServer()
    telemetry_server.start_data_listening_thread((cfg.telem_ip, cfg.telem_port))
    telemetry_server.start_video_listening_thread((cfg.video_ip, cfg.video_port))
    telemetry_server.run_flask(cfg.browser_port)
