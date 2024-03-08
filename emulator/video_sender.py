import cv2
import os
import imutils
import time
import numpy as np
import math
from glob import glob
from telemetry_server.sockets import Socket
from telemetry_server.config_parser import TelemServerConfig

print("Finished imports")

script_folder = os.path.dirname(os.path.abspath(__file__))


class FrameGenerator():
    def __init__(self, width, height, fps, noisy_background=False):
        self.cam_model = "Artificial"
        self.frames = []  # List of frames to be sent
        self.frame_counter = 0
        self.frame_width  = width
        self.frame_height = height
        self.grab_fps_cam = fps
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.font_scale = width/250
        self.font_thickness = math.ceil(width/200)
        self.text_color = (255, 255, 255)  # White color
        self.bg_color = (0, 0, 0)  # Black color
        self.noisy_background = noisy_background
    
    def get_next_frame(self):
        # Sleep
        time.sleep(1/self.grab_fps_cam)

        if self.noisy_background:
            # Create a white noise background
            frame = np.random.randint(0, 256, (self.frame_height, self.frame_width, 3), dtype=np.uint8)
        else:
            # Create a black image
            frame = np.zeros((self.frame_height, self.frame_width, 3), dtype=np.uint8)
            # frame.fill(0)

        # Add counter text
        counter_text = f"Counter: {self.frame_counter}"
        text_size, _ = cv2.getTextSize(counter_text, self.font, self.font_scale, self.font_thickness)
        text_x = (self.frame_width - text_size[0]) // 2
        text_y = (self.frame_height + text_size[1]) // 2
        cv2.putText(frame, counter_text, (text_x, text_y), self.font, self.font_scale, self.text_color, self.font_thickness, cv2.LINE_AA)
        
        self.frame_counter += 1

        return frame, self.frame_counter

# Create udp connection
cfg = TelemServerConfig(os.path.join("telemetry_server", "server_config.ini"))
video_channel = (cfg.video_send_ip, cfg.video_port)
print(f"Sending video to {video_channel[0]}:{video_channel[1]}")
video_sock = Socket(video_channel, big_buffer=True)

# TODO fragment big frames (noisy = True)
video_feeder = FrameGenerator(width=640, height=480, fps=10, noisy_background=False)

while True:
    # Get frame
    image, frame_num = video_feeder.get_next_frame()
    print(f"Sending {frame_num}", end="\r")

    # image = imutils.resize(image, width=400)
    _, buffer = cv2.imencode('.jpg',image,[cv2.IMWRITE_JPEG_QUALITY,80])
    
    cv2.imshow("Video", image)
    if cv2.waitKey(30) & 0xFF == ord('q'):
        break
    
    try:
        video_sock.send_serialized(buffer)
    except Exception as e:
        print(f"Failed to send buffer of size {len(buffer)}:\n{e}")

# video_folder=os.path.join(script_folder, "short_rec", "*.tiff")
# video_files_list = glob(video_folder, recursive=True)
# print(f"Found {len(video_files_list)} frames")

# for frame_path in video_files_list:
#     print(frame_path)

#     image = cv2.imread(frame_path, cv2.IMREAD_UNCHANGED)  # Read TIFF file without any modification
#     if image is None:
#         print(f"Unable to read file: {frame_path}")
#         continue
    
#     image = imutils.resize(image, width=400)

#     _, buffer = cv2.imencode('.jpg',image,[cv2.IMWRITE_JPEG_QUALITY,80])
    
#     cv2.imshow("Video", image)
#     if cv2.waitKey(30) & 0xFF == ord('q'):
#         break
    
#     video_sock.send_serialized(buffer)

print("Finish")