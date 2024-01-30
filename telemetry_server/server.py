from flask import Flask, render_template,Response,request
from flask_socketio import SocketIO,send,emit
# import rida_parser as rida
# import cv2

# from config import *

app = Flask(__name__, static_url_path='', static_folder='../openmct/dist', template_folder='templates')

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


# def simulate_udp_transmissions(msg:rida.MessageTransmitter):
#     from glob import glob
#     transmitter = rida.MessageTransmitter(msg)
#     while True:
#         for file_name in glob("recordings/*.bin"):
#             transmitter.transmit_file(file_name)

# @app.route ('/video-frame/<video_path>/<frame_number>')
# def get_video_frame (video_path, frame_number):
#     width = request.args.get('w')
#     height = request.args.get('h')
#     cap = cv2.VideoCapture(video_path)
#     cap.set(cv2.CAP_PROP_POS_FRAMES, float(frame_number))
#     ret, frame = cap.read()
#     if ret:
#         _, buffer = cv2.imencode('.jpg', frame)
#         frame = buffer.tobytes()
#         out = Response(buffer.tobytes(),mimetype='image/jpeg')
#     else:
#         out = Response(b'',mimetype='image/jpeg')
#     cap.release()
#     return out

# def handle_udp_data_message (messages,receiver:rida.MessageReceiver):
#     with app.app_context():
#         if messages:
#             print("d",end="",flush=True)
#             socketio.emit("realtime",messages)

# def handle_udp_video (frame,timestamp,receiver:rida.MessageReceiver):
#     with app.app_context():
#         if frame:
#             print("v",end="",flush=True)
#             socketio.emit("frame",{"data":frame, "timestamp":timestamp})

# history_frames = []
# def handle_video_frame_counter_change (msg:rida.Message, cur_frame_number, last_frame_counter, cur_timestamp):
#     pass
    # import base64
    # if last_frame_counter == 0:
    #     frame_handler["first_frame_counter"] = cur_frame_number
    
    # with open("frame.jpg","rb") as f:
    #     frame =  bytes(f.read())
    #     try:
    #         cur_data = {
    #             "data":frame,
    #             "timestamp":cur_timestamp,
    #             "frame_num":cur_frame_number
    #         }
    #         socketio.emit("image", frame)
            
    #     except:
    #         pass
    #     if len(history_frames)> (30 * 60): # one minute of video history
    #         history_frames.pop()


    # print (f"Current vide frame = {cur_frame_number - frame_handler["first_frame_counter"]}")

import socket
import json
import datetime
class UDP_Listener():
    def __init__(self):
        self.buf_size = 65535
        self.udp_dashboard_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # self.udp_dashboard_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.udp_dashboard_sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, self.buf_size)
        self.listen = True
    
    def start_data_listening(self):
        address = ("127.0.0.1", 50020)
        self.udp_dashboard_sock.bind(address)

        print(f"Listening telemetry on {address[0]}:{address[1]}")

        while self.listen:
            data, _ = self.udp_dashboard_sock.recvfrom(65535) # Blocking. Should be in thread
            
            timestamp = datetime.datetime.now().timestamp() * 1000

            # Get and save the msg with timestamp
            msg_dict = json.loads(data.decode())
            # print(msg_dict, flush=True)
            msg_dict["timestamp"] = timestamp
            historic_data.append(msg_dict)
            
            # Cyclic buffer like
            if len(historic_data) > historic_data_max_size:
                historic_data.pop(0)
            
            # Build message to send to OpenMCT
            realtime_msg_to_send = {}
            for key, value in msg_dict.items():
                # Get all subscribed elemnts 
                if key in subscribed_keys.keys():
                    realtime_msg_to_send[key] = value
                
            # If anything to show
            if realtime_msg_to_send:
                realtime_msg_to_send["timestamp"] = timestamp

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

# TODO subscribe
        

if __name__ == '__main__':

    import threading

    receiver = UDP_Listener()

    # receiver = rida.MessageReceiver (message,10000)
    # receiver.add_udp_data_listener(handle_udp_data_message)
    
    threading.Thread(target=receiver.start_data_listening, daemon=True).start()
    
    browser_port = 3000
    print(f"Running on http://localhost:{browser_port}/index.html")

    socketio.run(app, debug=True, use_reloader=False, port=browser_port)


    