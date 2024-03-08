import cv2
import os
import imutils
from glob import glob
from telemetry_server.sockets import Socket
from telemetry_server.config_parser import TelemServerConfig

print("Finished imports")

script_folder = os.path.dirname(os.path.abspath(__file__))

# Create udp connection
cfg = TelemServerConfig(os.path.join("telemetry_server", "server_config.ini"))
video_channel = (cfg.video_send_ip, cfg.video_port)
print(f"Sending video to {video_channel[0]}:{video_channel[1]}")
video_sock = Socket(video_channel, big_buffer=True)

video_folder=os.path.join(script_folder, "short_rec", "*.tiff")
video_files_list = glob(video_folder, recursive=True)
print(f"Found {len(video_files_list)} frames")

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
    
    video_sock.send_serialized(buffer)

print("Finish")