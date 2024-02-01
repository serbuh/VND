from flask import Flask, render_template,Response,request
from flask_socketio import SocketIO,send,emit
import socket
import json
import datetime
import threading

app = Flask(__name__, static_url_path='', static_folder='../openmct/dist', template_folder='templates')

app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

historic_data = []
subscribed_keys = {}
historic_data_max_size = 1000

@socketio.on("subscribe")
def handle_subscribe(key):
    print(f"Subscribe req: {key}")
    subscribed_keys[key] = True

@socketio.on("unsubscribe")
def handle_unsubscribe(key):
    print(f"Unsubscribe req: {key}")
    subscribed_keys.pop(key, None)

@app.route('/history/<key>/<start>/<end>/<strategy>/<size>')
def handle_historic_data(key, start, end, strategy, size):
    historic_blob = []
    for msg_batch in historic_data:
        if msg_batch["timestamp"] > float(start) and msg_batch["timestamp"] < float(end):
            for stored_key, value in msg_batch.items(): # Extract the item
                if stored_key == key: # Find needed key
                    historic_msg = {"id": stored_key, "value": value, "timestamp": msg_batch["timestamp"], "mctLimitState":None}
                    # print(f"One of the historic msgs: {historic_msg}")
                    historic_blob.append(historic_msg)
    print(f"Send {len(historic_blob)} history items for {key}")
    return historic_blob

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

            # New telemetry message
            msg_batch = json.loads(data.decode())
            #print(msg_batch, flush=True)

            # Send message to OpenMCT
            with app.app_context():
                msgs_to_emit = []
                
                # Fetch messages that the openmct is subscribed for
                for msg_key, msg_value in msg_batch.items():
                    if subscribed_keys.get(msg_key):
                        msgs_to_emit.append({"id": msg_key, "value": msg_value, "timestamp":timestamp, "mctLimitState": None})

                # Print emit realtime message
                if msgs_to_emit:
                    # print("d",end="",flush=True)
                    print(f"Send realtime msgs: {msgs_to_emit}")
                    socketio.emit("realtime", msgs_to_emit)
            
            # Save history
            msg_batch["timestamp"] = timestamp # append timestamp
            historic_data.append(msg_batch) # [{"field_1": 1, "field_2": 2, "timestamp":timestamp}, {...}, ...]
            
            # Cyclic buffer like
            if len(historic_data) > historic_data_max_size:
                historic_data.pop(0)

        

if __name__ == '__main__':
    # Params
    address_listen_to = ("127.0.0.1", 50020)
    browser_port = 3000

    # Start Telemetry listener
    telemetry_server = TelemetryServer()
    telemetry_server.start_data_listening_thread(address_listen_to)
    telemetry_server.run_flask(browser_port)
    