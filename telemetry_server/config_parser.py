import configparser
import os

class TelemServerConfig():
    def __init__(self, ini_file):
        config = configparser.ConfigParser()
        if not os.path.isfile(ini_file):
            print(f"File does not exist: {ini_file}")
            exit()
        
        config.read(ini_file)

        self.browser_port = int(config['Comm']['browser_port'])
        self.listen_to_ip = config['Comm']['listen_to_ip']
        self.listen_to_port = int(config['Comm']['listen_to_port'])

if __name__ == "__main__":
    script_folder = os.path.dirname(os.path.abspath(__file__))
    cfg = TelemServerConfig(os.path.join(script_folder, "server_config.ini"))
    print(f"Browser port: {cfg.browser_port}" )