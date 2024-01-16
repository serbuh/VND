import typing
import os
import json

class JSON_Creator():
    def __init__(self):
        # Constant output file
        self.out_file = os.path.join("..", "..", "openmct", "telemetry_plugin", "openmct_interface.json")
    
    def geberate_json_from_path(self, fullpath):
        with open(fullpath) as in_f:
            in_lines = in_f.read()
            
            self.generate_json_from_lines(in_lines)
    
    def generate_json_from_lines(self, in_lines:str):            
            
            in_lines = in_lines.splitlines() # Split the lines with \n

            print(f"Writing resuls to json: {self.out_file}")
            
            with open(self.out_file, "w") as out_f:

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

    def write_lines_to_json(self, in_lines, out_f:typing.TextIO) -> None:
        
        dictionary = {
            "name": "PredefinedTelemetry",
            "key": "pl",
            "measurements": []
        }

        # Iterate over each field name
        print("Fields:")
        for i, field_name in enumerate(in_lines):
            # Remove new line symbol
            field_name = field_name.strip("\n")

            # String handling
            string_prefix = "S:"
            if field_name.startswith(string_prefix):
                field_name = field_name[len(string_prefix):]
                open_mct_type = "string"
            else:
                open_mct_type = "number"
            print(f"{open_mct_type}: {field_name}")

            measurement = self._generate_measurement(field_name, open_mct_type)
            dictionary["measurements"].append(measurement)

        # Serializing json
        json_object = json.dumps(dictionary, indent=4)

        out_f.write(json_object)

    def _generate_measurement(self, field_name, open_mct_type):
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
        return measurement



if __name__ == "__main__":
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
    json_creator = JSON_Creator()
    json_creator.geberate_json_from_path(fullpath)


# TODO enums
"""
        {
            "name": "Status.StateEnum",
            "key": "Status.StateEnum",

            "values": [
                {

                    "key": "value",
                    "name": "Value",
                    "units": "unit",
                    "format": "enum",
                    "hints": {
                        "range": 1
                    },
                    "enumerations": [
                        {
                            "string": "BAD",
                            "value": "0"
                        },
                        {
                            "string": "NORMAL",
                            "value": "1"
                        },
                        {
                            "string": "GOOD",
                            "value": "2"
                        }
                    ]
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
        },
"""