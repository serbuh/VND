import configparser
import os

class TelemServerConfig():
    def __init__(self, ini_file):
        self.ini_file = ini_file
        self.config = configparser.ConfigParser()
        if not os.path.isfile(ini_file):
            print(f"File does not exist: {ini_file}")
            exit()
        
        self.config.read(ini_file)

        self.browser_port = int(self.config['Comm']['browser_port'])

        # Telem channel
        self.telem_ip = self.config['Comm']['telem_ip']
        self.telem_port = int(self.config['Comm']['telem_port'])

        # Video channel
        self.video_ip = self.config['Comm']['video_ip']
        self.video_port = int(self.config['Comm']['video_port'])

        # Emulator sending:
        self.telem_send_ip = self.config['Emulator']['telem_send_ip']
        self.video_send_ip = self.config['Emulator']['video_send_ip']

    def print_summary(self):
        print(f"Listening for telemetry on   {self.telem_ip}:{self.telem_port}")
        print(f"Listening for video on   {self.video_ip}:{self.video_port}")
        print(f"Browser address:   localhost:{self.browser_port}")
    
    def write_to_file(self):
        print("Rewriting config!")
        self.print_summary()
        self.config['Comm']['browser_port'] = self.browser_port
        self.config['Comm']['telem_ip']     = self.telem_ip
        self.config['Comm']['telem_port']   = self.telem_port
        self.config['Comm']['video_ip']     = self.video_ip
        self.config['Comm']['video_port']   = self.video_port

        self.config['Emulator']['telem_send_ip'] = self.telem_send_ip
        self.config['Emulator']['video_send_ip'] = self.video_send_ip
        
        with open(self.ini_file, "wt", encoding='utf-8') as f:
            self.config.write(f)

if __name__ == "__main__":
    script_folder = os.path.dirname(os.path.abspath(__file__))
    cfg = TelemServerConfig(os.path.join(script_folder, "server_config.ini"))
    print(f"Browser port: {cfg.browser_port}" )