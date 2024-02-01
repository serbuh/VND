from flask import Flask, render_template,Response,request
from flask_socketio import SocketIO,send,emit
import socket
import json
import datetime
import threading

app = Flask(__name__, static_url_path='', static_folder='../openmct', template_folder='templates')

app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

historic_data = []
subscribed_keys = {}
historic_data_max_size = 1000

@socketio.on("subscribe")
def handle_subscribe(key):
    print(f"Subscribe to {key}")
    subscribed_keys[key] = True

@socketio.on("unsubscribe")
def handle_unsubscribe(key):
    print(f"Unsubscribe from {key}")
    del subscribed_keys[key]


def get_historic_data(requested_key, from_timestamp, to_timestamp):
    out = []

    for msg_dict in historic_data:
        if msg_dict["timestamp"] > from_timestamp and msg_dict["timestamp"] < to_timestamp:
            current_object = {}
            for key, value in msg_dict.items():
                if key == requested_key:
                    current_object[key] = value
            if current_object:
                current_object["timestamp"] = msg_dict["timestamp"]
                out.append(current_object)

    return out

@app.route('/CVASHistory/<key>') 
def handle_historic_data(key):
    start = request.args.start
    end = request.args.end
    data = get_historic_data(key,float(start),float(end))
    
    return data

class TelemetryServer():
    def __init__(self):
        self.buf_size = 65535
        self.udp_dashboard_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # self.udp_dashboard_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.udp_dashboard_sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, self.buf_size)
        self.listen = True
    
    def run_flask(self, browser_port):
        print(f"Running on http://localhost:{browser_port}/index.html")
        socketio.run(app, debug=True, use_reloader=False, port=browser_port)

    def start_data_listening_thread(self, address_listen_to):
        # Start listening for telemetry
        threading.Thread(target=self.start_data_listening, args=(address_listen_to,), daemon=True).start()

    def start_data_listening(self, address_listen_to):
        self.udp_dashboard_sock.bind(address_listen_to)

        print(f"Listening telemetry on {address_listen_to[0]}:{address_listen_to[1]}")

        while self.listen:
            data, _ = self.udp_dashboard_sock.recvfrom(65535) # Blocking. Should be in thread
            
            timestamp = datetime.datetime.now().timestamp() * 1000

            # Get and save the msg with timestamp
            msg_dict = json.loads(data.decode())
            
            # Print incoming messages
            #print(msg_dict, flush=True)
            
            msg_dict["timestamp"] = timestamp
            historic_data.append(msg_dict)
            
            # Cyclic buffer like
            if len(historic_data) > historic_data_max_size:
                historic_data.pop(0)
            
            # Build message to send to OpenMCT
            realtime_msg_to_send = []
            for key, value in msg_dict.items():
                # Get all subscribed elemnts 
                if key in subscribed_keys.keys():
                    realtime_msg_to_send.append({"key": key, "value": value, "timestamp": timestamp})

            # Send message to OpenMCT
            with app.app_context():
                print("d",end="",flush=True)
                socketio.emit("realtime", realtime_msg_to_send)

            # TODO Bundling
            # if counter >= realtime_message_list_size:
            #     for _,handler in self.realtime_listeners.items():
            #         handler(message_buffer,self)
            #         message_buffer = []
            #         counter = 0
        

if __name__ == '__main__':
    # Params
    address_listen_to = ("127.0.0.1", 50020)
    browser_port = 3000

    # Start Telemetry listener
    telemetry_server = TelemetryServer()
    telemetry_server.start_data_listening_thread(address_listen_to)
    telemetry_server.run_flask(browser_port)
    