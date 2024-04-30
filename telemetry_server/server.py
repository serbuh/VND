from flask import Flask, request, redirect, url_for
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
import time

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
        self.dump_folder_name = "saved_experiments"

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
            print(f"Currently subscribed {self.subscribed_keys.keys()}")

        @self.socketio.on("unsubscribe")
        def handle_unsubscribe(key):
            print(f"Unsubscribe req: {key}")
            self.subscribed_keys.pop(key, None)
            print(f"Currently subscribed {self.subscribed_keys.keys()}")

        @self.flask_server.route('/')
        def static_file():
            return self.flask_server.send_static_file('index.html')
        
        ##### Control page functions #####
        @self.flask_server.route('/control')
        def control_page():
            status_message = request.args.get('status_message')
            return '''
            <html>
            <body>
                <h1>Experiment</h1>
                <form action="/save_experiment" method="post">
                    <input type="text" name="save_postfix" placeholder="Experiment name">
                    <button type="submit">Save</button><br>
                </form>
                <form action="/clear_experiment" method="post">
                    <button type="submit">Clear</button><br>
                </form>
                <form action="/load_experiment" method="post">
                    <input type="file" name="load_path" id="file">
                    <button type="submit">Load</button><br>
                </form>
                <p>Status: {}</p>
            </body>
            </html>
            '''.format(status_message if status_message else '')

        @self.flask_server.route('/save_experiment', methods=['POST'])
        def save_experiment_function():
            save_postfix = request.form['save_postfix']
            # Dump historic data to file
            status = self.save_historic_data(save_postfix)
            print(status)
            return redirect(url_for('control_page', status_message=status))
        
        @self.flask_server.route('/clear_experiment', methods=['POST'])
        def clear_experiment_function():
            # Dump historic data to file
            status = self.clear_historic_data()
            print(status)
            return redirect(url_for('control_page', status_message=status))
        
        @self.flask_server.route('/load_experiment', methods=['POST'])
        def load_experiment_function():
            load_path = request.form['load_path']
            # Load historic data from file
            status = self.load_historic_data(load_path)
            print(status)
            return redirect(url_for('control_page', status_message=status))
        ##### End of control page functions #####

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

    def start_ticking_thread(self):
        # Start ticking with remote clock
        threading.Thread(target=self.start_ticking, daemon=True).start()

    def start_ticking(self):
        while self.listen:
            timestamp = datetime.datetime.now().timestamp() * 1000
            # Emit realtime video to OpenMCT
            with self.flask_server.app_context():
                self.socketio.emit("realtime-tick", {"timestamp": timestamp})
            time.sleep(1)
            

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
            # if len(self.historic_data) > self.historic_data_max_size:
            #     self.historic_data.pop(0)
    
    def load_historic_data(self, file_path):
        full_file_path = os.path.join(self.dump_folder_name, file_path)
        # Create folder if not exist
        if not os.path.isfile(full_file_path):
            return f"No such file {full_file_path}"
        
        return f"Loaded file {full_file_path}"

    def clear_historic_data(self):
        self.historic_data = []
        return "Cleared history"

    def save_historic_data(self, save_postfix=""):
        # Do nothing if no historic data present
        if not len(self.historic_data):
            return "Empty experiment. Nothing to save"
        
        # Create folder if not exist
        if not os.path.exists(self.dump_folder_name):
            os.makedirs(self.dump_folder_name)

        # Calculate start and stop timestamps
        start_millisec = self.historic_data[0]['timestamp']
        stop_millisec = self.historic_data[-1]['timestamp']
        f_year, f_month, f_day, f_hour, f_minute, f_sec = self.convert_millisec_to_date_string(start_millisec)
        duration_minutes = round((stop_millisec - start_millisec) / 1000 / 60, 1)
        
        # Give experiment a name
        if save_postfix:
            save_postfix = "_" + save_postfix
        experiment_name = f"dump_{f_year}-{f_month}-{f_day}__{f_hour}-{f_minute}-{f_sec}__{duration_minutes}_min{save_postfix}.pkl"
        full_rel_path = os.path.join(self.dump_folder_name, experiment_name)

        # Dump history to file
        with open(full_rel_path, 'wb') as f:
            pickle.dump(self.historic_data, f)

        # Return experiment name
        return f"Saved {full_rel_path}"
            
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
    telemetry_server.start_ticking_thread()
    telemetry_server.run_flask(cfg.browser_port)
