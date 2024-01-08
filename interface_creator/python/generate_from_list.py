from typing import TextIO
import os

# Constant output file
out_file = os.path.join("..", "..", "openmct", "messages_interface", "openmct_interface.json")

# Global
prefix = """{
    "name": "CVAS",
    "key": "pl",
    "measurements": [
"""

# Global
postfix = """
    ]
}
"""

def get_field_desc(key_name, type):
    # Replace spaces
    key_name = key_name.replace(" ", "_")
    
    return ( \
"        {\n"
f'            "name": "{key_name}",\n'
f'            "key": "{key_name}",\n'
'''
            "values": [
                {
                    "key": "value",
                    "name": "Value",
                    "units": "unit",
'''
f'                    "format": "{type}",\n'
'''                    "hints": {
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
        }'''
    )

def generate_openmct_json(in_lines:str):
    in_lines = in_lines.splitlines() # Split the lines with \n

    print(f"Writing resuls to json: {out_file}")
    
    with open(out_file, "w") as out_f:

        # Write prefix
        out_f.write(prefix)

        # Iterate over each field name
        print("Fields list:")
        for i, field_name in enumerate(in_lines):
            # Remove new line symbol
            field_name = field_name.strip("\n")

            # String handling
            string_prefix = "S:"
            if field_name.startswith(string_prefix):
                field_name = field_name[len(string_prefix):]
                open_mct_type = "string"
            else:
                open_mct_type = "integer"
            print(f"{open_mct_type}: {field_name}")

            # write
            out_f.write(get_field_desc(field_name, open_mct_type))

            # Add comma only in between the field description dicts
            if i != len(in_lines) - 1:
                out_f.write(",\n")

        # Write postfix
        out_f.write(postfix)

    print("FINISHED")

def get_files_from_folder(interfaces_folder):
    '''
    Get the list of available txt files
    '''
    fullpaths = [os.path.join(interfaces_folder, f) for f in os.listdir(interfaces_folder) if f.lower().endswith('.txt')]
    filenames = [f for f in os.listdir(interfaces_folder) if f.lower().endswith('.txt')]
    return filenames, fullpaths

if __name__ == "__main__":
    interfaces_folder = os.path.join(".", "examples")
    filenames, fullpaths = get_files_from_folder(interfaces_folder)
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

    with open(fullpath) as in_f:
        in_lines = in_f.read()
        generate_openmct_json(in_lines)
