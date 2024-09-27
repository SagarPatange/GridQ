import random
import json


def load_from_json(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
    return data

def json_to_element_list (json_string):

    # Convert the string into a dictionary
    json_dict = json.loads(json_string)

    # Create the list with alternating keys and values
    elements_list = []
    for key, value in json_dict.items():
        # Convert value to float if possible
        try:
            value = float(value)
        except ValueError:
            pass
        elements_list.append(key)
        elements_list.append(value)

    return elements_list

