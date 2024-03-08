import socket
import cv2
import os
import json
import imutils
from glob import glob
from telemetry_server.sockets import Socket
print("Finished imports")

# Create udp connection
video_channel = ("127.0.0.1", 5566)
print(f"Sending video to {video_channel[0]}:{video_channel[1]}")
video_sock = Socket(video_channel, big_buffer=True)

video_folder=os.path.join("emulator", "elyakim_short", "*.tiff")
video_files_list = glob(video_folder, recursive=True)

for frame_path in video_files_list:
    print(frame_path)
    image = cv2.imread(frame_path, cv2.IMREAD_UNCHANGED)  # Read TIFF file without any modification
    if image is None:
        print(f"Unable to read file: {frame_path}")
        continue
    
    image = imutils.resize(image, width=400)

    _, buffer = cv2.imencode('.jpg',image,[cv2.IMWRITE_JPEG_QUALITY,80])
    
    cv2.imshow("Video", image)
    if cv2.waitKey(30) & 0xFF == ord('q'):
        break
    
    video_sock.send(buffer)

print("Finish")