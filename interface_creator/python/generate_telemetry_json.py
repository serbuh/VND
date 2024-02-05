import typing
import os
import json

class JSON_Creator():
    def __init__(self, interface_file, port_file):
        # Constant output file
        self.interface_file = interface_file
        self.port_file = port_file

        # Check existence of port config file
        if not os.path.exists(self.interface_file):
            print(f'Interface file does not exist!: {self.interface_file}')
            return
    
        # Check existence of port config file
        if not os.path.exists(self.port_file):
            print(f'Port config file does not exist!: {self.port_file}')
            return
        
    def geberate_json_from_path(self, fullpath):
        with open(fullpath) as in_f:
            in_lines = in_f.read()
            
            self.generate_json_from_lines(in_lines)
    
    def generate_json_from_lines(self, in_lines:str):            
            
            in_lines = in_lines.splitlines() # Split the lines with \n

            print(f"Writing resuls to json: {self.interface_file}")
            
            with open(self.interface_file, "w") as out_f:

                self.write_lines_to_json(in_lines, out_f)
            
            print("FINISHED")

    @staticmethod
    def get_files_from_folder(interfaces_folder):
        '''
        Get the list of available txt files
        '''
        fullpaths = [os.path.join(interfaces_folder, f) for f in os.listdir(interfaces_folder) if f.lower().endswith('.txt')]
        filenames = [f for f in os.listdir(interfaces_folder) if f.lower().endswith('.txt')]
        return fullpaths, filenames

    def _enum_parse(self, line, enum_prefix):
        field_name = line[len(enum_prefix):] # Cut off prefix
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

    def write_lines_to_json(self, in_lines, out_f:typing.TextIO) -> None:
        
        dictionary = {
            "name": "PredefinedTelemetry",
            "key": "pl",
            "measurements": []
        }

        # Prefixes definition
        string_prefix = "S:"
        enum_prefix = "E:"
        
        # Iterate over each field name
        print("Fields:")
        for line in in_lines:
            # Remove new line symbol
            line = line.strip("\n")

            # Handle types
            if line.startswith(string_prefix): # String
                field_name = line[len(string_prefix):] # Cut off prefix
                measurement = self._generate_measurement(field_name, "string")

            elif line.startswith(enum_prefix): # Enum
                field_name, enum_values = self._enum_parse(line, enum_prefix)
                measurement = self._generate_measurement(field_name, "enum", enum_values)

            else: # Number
                measurement = self._generate_measurement(line, "number")

            dictionary["measurements"].append(measurement)

        # Serializing json
        json_object = json.dumps(dictionary, indent=4)

        out_f.write(json_object)

    def get_port_from_file(self):
        with open(self.port_file, "rt", encoding='utf-8') as f:
            port_input = f.read()
            port_input = str(int(port_input))
        return port_input

    def set_port_to_file(self, port):
        with open(self.port_file, "wt", encoding='utf-8') as f:
            print(f"Setting port to {port}")
            f.write(port)

    def _generate_measurement(self, field_name, open_mct_type, enum_values=None):
        # Replace spaces in field names (for the json)
        field_name = field_name.replace(" ", "_")
        
        measurement = {
            "name": field_name,
            "key": field_name,
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

            print(f"{open_mct_type}: {field_name} ({enum_values_str})")
        else:
            print(f"{open_mct_type}: {field_name}")
        
        return measurement



if __name__ == "__main__":
    interface_file = os.path.join("..", "..", "openmct", "telemetry_plugin", "openmct_interface.json")
    port_file = os.path.join("..", "..", "telemetry_server", "port_config.txt")
    json_creator = JSON_Creator(interface_file, port_file)
    
    # Set port
    current_port = json_creator.get_port_from_file()
    choice_port = input(f"Listening to telemetry on port {current_port}. Change port? [y/N]")

    if choice_port in ["y", "Y"]:
        new_port = input("Enter port\n")
        json_creator.set_port_to_file(new_port)

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
    json_creator = JSON_Creator(interface_file, port_file)
    json_creator.geberate_json_from_path(fullpath)
