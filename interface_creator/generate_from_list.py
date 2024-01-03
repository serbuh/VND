from typing import TextIO
import os

# Constant output file
out_file = os.path.join("..", "openmct", "messages_interface", "CVASdictionary.json")

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


if __name__ == "__main__":
    in_file = "fields_in.txt"

    print(f"Reading fields from {in_file}")

    with open(in_file) as in_f:
        in_lines = in_f.readlines()

        generate_openmct_json(in_lines)
