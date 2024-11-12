import typing
import os
import json
import configparser
from telemetry_server.config_parser import TelemServerConfig

class Folder():
    '''
    Class that mimics the folders structure
    '''
    def __init__(self, name):
        self.name = name
        self.children = []

    def add_chain(self, folder_chain:list):
        '''
        Create folder structure from list of nested folders
        '''
        # Stop condition - empty list
        if not folder_chain:
            return
        
        # Get current folder and the rest of the chain
        curr_folder = folder_chain[0]
        rest_of_chain = folder_chain[1:]

        # Create folder if not exist
        existing_child = self.get_child_by_name(curr_folder)

        if not existing_child:
            existing_child = Folder(curr_folder) # Create
            self.children.append(existing_child) # Append to current
        
        existing_child.add_chain(rest_of_chain) # Continue to the newly added
    
    def get_child_by_name(self, name):
        for child in self.children:
            if child.name == name:
                return child
        return None

    def print_tree(self, prefix=""):
        print(f"{prefix}{self.name}")
        for child in self.children:
            child.print_tree(prefix=f"  {prefix}")
        
    def get_folders_objects_list(self, parent_chain=None):

        if parent_chain is None:
            parent_chain = []
        
        folders_list = []
        current_chain = parent_chain
        for child in self.children:
            current_chain = parent_chain.copy() # Rewrite chain for each child
            if current_chain:
                folders_list.append({
                    "name": child.name,
                    "key": ".".join(current_chain) + "." + child.name,
                    "nested_under": ".".join(current_chain),
                })
            else:
                folders_list.append({
                    "name": child.name,
                    "key": child.name,
                    "nested_under": "RootFolder",
                })

            current_chain.append(child.name)
            folders_list.extend(child.get_folders_objects_list(current_chain))

        return folders_list

class JSON_Creator():
    def __init__(self, interface_file, server_config):
        # Constant output file
        self.interface_file = interface_file
        self.server_config = server_config

        # Prefixes definition
        self.string_prefix = "S:"
        self.enum_prefix = "E:"
        self.version_prefix = "Ver:"
        self.root_name_prefix = "Root:"

        self.folder_hierarchy = Folder("RootFolder")

        # Check existence of port config file
        if not os.path.exists(self.interface_file):
            print(f'Interface file does not exist!: {self.interface_file}')
            return
    
        # Check existence of port config file
        if not os.path.exists(self.server_config):
            print(f'Port config file does not exist!: {self.server_config}')
            return
        
    def generate_json_from_path(self, fullpath) -> bool:
        with open(fullpath) as in_f:
            in_lines = in_f.read()
            
            success = self.generate_json_from_lines(in_lines)
            return success
    
    def generate_json_from_lines(self, in_lines:str) -> bool:            
        in_lines = in_lines.splitlines() # Split the lines with \n

        print(f"Writing results to json: {self.interface_file}")

        # Create the directory if it doesn't exist
        os.makedirs(os.path.dirname(self.interface_file), exist_ok=True)
        with open(self.interface_file, "w") as out_f:
            update_interface_result = self.write_lines_to_json(in_lines, out_f)

        if not update_interface_result:
            print("Failed to update interface")
            return update_interface_result

        print("Interface updated successfully")

        # Read version
        with open(self.interface_file, "r") as json_f:
            resulting_json = json.load(json_f)
            ver = resulting_json.get("version", None)
            if ver is None:
                print(f"Interface version is not specified. Use '{self.version_prefix}' to specify version")
            else:
                print(f"Interface version: {ver}")

        return update_interface_result

    @staticmethod
    def get_files_from_folder(interfaces_folder):
        '''
        Get the list of available txt files
        '''
        fullpaths = [os.path.join(interfaces_folder, f) for f in os.listdir(interfaces_folder) if f.lower().endswith('.txt')]
        filenames = [f for f in os.listdir(interfaces_folder) if f.lower().endswith('.txt')]
        return fullpaths, filenames

    def _enum_parse(self, line):
        field_name = line[len(self.enum_prefix):] # Cut off prefix
        rpart = field_name.rpartition("{")
        field_name = rpart[0] # take name before enum values ( "{...}" )
        field_name = field_name.strip(" ") # Cut off whitespaces before and after field_name

        # Parsing enum values
        # NOTE: chose not to use json parsing here in order to avoid double quoutes for keys and values (i.e. {GOOD:0} instead of {"GOOD":"0"})
        enum_values = rpart[2] # Get enum as a one string that ends with }
        if not enum_values.endswith("}"):
            print(f"Error. Enum parsing failed. Check syntax for:\nName: {rpart[0]}\nShould be between two curly braces: {rpart[1] + rpart[2]}")
            exit()
        enum_values = enum_values.strip("}") # Remove closing curly brace
        enum_values = enum_values.split(",") # split to the list of values (comma separated)
        enum_values = [ enum_val.strip(" ") for enum_val in enum_values ] # Strip whitespaces before and after
        enum_values = [ enum_val.split(":") for enum_val in enum_values ]
        # Syntax check
        for enum_val in enum_values:
            if len(enum_val) != 2:
                print(f"Error in field {field_name}: Wrong enum val: {enum_val}")
                exit()

        return field_name, enum_values

    def write_lines_to_json(self, in_lines, out_f:typing.TextIO) -> bool:
        
        dictionary = {
            "version": None,    # ICD version
            "name": None,       # root name
            "measurements": []  # telemetry measurements
        }
        
        # Iterate over each field name
        print("Fields:")
        measurements = []
        for line in in_lines:
            # Remove new line symbol
            line = line.strip("\n")

            # Handle types
            if line.startswith(self.string_prefix): # String
                field_name = line[len(self.string_prefix):] # Cut off prefix
                measurement = self._generate_measurement(field_name, "string")

            elif line.startswith(self.enum_prefix): # Enum
                field_name, enum_values = self._enum_parse(line)
                measurement = self._generate_measurement(field_name, "enum", enum_values)

            elif line.startswith(self.version_prefix): # Version
                version = line[len(self.version_prefix):] # Cut off prefix
                
                if dictionary.get("version") is None:
                    print(f"Interface version: {version}")
                    dictionary["version"] = version
                else:
                    print(f"Version specified at least twice: {dictionary['version']}, {version}")
                    return False
                continue

            elif line.startswith(self.root_name_prefix): # Root name
                root_name = line[len(self.root_name_prefix):] # Cut off prefix
                dictionary['name'] = root_name
                continue

            else: # Number
                measurement = self._generate_measurement(line, "number")

            measurements.append(measurement)

        # Build folder hierarchy in JSON
        folder_list = self.build_folder_objects()

        # Add folder hierarchy and the telemetry points to the JSON
        dictionary["measurements"].extend(folder_list)
        dictionary["measurements"].extend(measurements)

        
        # Serializing json
        json_object = json.dumps(dictionary, indent=4)

        out_f.write(json_object)

        return True

    def _generate_measurement(self, field_name, open_mct_type, enum_values=None):
        # Replace spaces in field names (for the json)
        field_key = field_name.replace(" ", "_")
        
        # field_name - take only the last part of the string that is separated by dot
        # folder_path - separated by dot.
        #                            E.g.:
        path = field_key.split(".")      # A.B.C.d
        field_name = path[-1]            # d
        folders_path = path[:-1]         # A.B.C
        parent_folder = folders_path[-1] # C
        
        self.folder_hierarchy.add_chain(folders_path)

        # If no parent folder - nest under root
        if not parent_folder:
            parent_folder = "RootFolder"
        
        measurement = {
            "name": field_name,
            "key": field_key,
            "nested_under": ".".join(folders_path),
            "values": [
                {
                    "key": "value",
                    "name": "Value",
                    "units": "unit",
                    "format": open_mct_type,
                    "hints": {
                        "range": 1
                    }
                },
                {
                    "key": "utc",
                    "source": "timestamp",
                    "name": "Timestamp",
                    "format": "utc",
                    "hints": {
                        "domain": 1
                    }
                }
            ]
        }
        if enum_values is not None:
            measurement["values"][0]['enumerations'] = []
            enum_values_str = ""
            for e_val in enum_values:
                enum_value_dict = {"string": e_val[0], "value": e_val[1]}
                measurement["values"][0]['enumerations'].append(enum_value_dict)
                enum_values_str += f" {e_val[0]}:{e_val[1]} "

            print(f"{open_mct_type}: {field_key} ({enum_values_str})")
        else:
            print(f"{open_mct_type}: {field_key}")
        
        return measurement

    def build_folder_objects(self):
        self.folder_hierarchy.print_tree()
        folders_list = self.folder_hierarchy.get_folders_objects_list() # TODO except root
        return folders_list

if __name__ == "__main__":
    interface_file = os.path.join("..", "..", "openmct", "telemetry_plugin", "openmct_interface.json")
    server_config = os.path.join("..", "..", "telemetry_server", "server_config.ini")
    json_creator = JSON_Creator(interface_file, server_config)
    
    # Read config
    cfg = TelemServerConfig(os.path.join("telemetry_server", "server_config.ini"))
    cfg.print_summary()
    
    # Set port
    choice_port = input(f"Listening to telemetry on port {cfg.browser_port}. Change port? [y/N]")

    if choice_port in ["y", "Y"]:
        cfg.browser_port = input("Browser port:\n")
        cfg.telem_ip = input("Telemetry ip:\n")
        cfg.telem_port = input("Telemetry port:\n")
        cfg.video_ip = input("Video ip:\n")
        cfg.video_port = input("Video port:\n")

        cfg.write_to_file()

    # Set interface
    interfaces_folder = os.path.join(".", "examples")
    fullpaths, filenames = JSON_Creator.get_files_from_folder(interfaces_folder)    
    print("Available files:")
    for num, filename, fullpath in zip(enumerate(filenames), filenames, fullpaths):
        print(f"{num[0]:>4} : {filename}")
    choice = input(f"Choose file number:")
    
    try:
        choice = int(choice)
        fullpath = fullpaths[choice]
        filename = filenames[choice]
    except:
        print(f"No such number: {choice}")
        exit()
    
    approve = input(f"Will use <{filename}> [Y/n]")
    if approve not in ["y", "Y", ""]:
        print("Exit.")
        exit()

    print(f"Reading fields from {filename}")

    # Create json
    json_creator = JSON_Creator(interface_file, server_config)
    success = json_creator.generate_json_from_path(fullpath)
