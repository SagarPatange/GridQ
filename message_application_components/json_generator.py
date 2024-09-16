import random
import json


def load_from_json(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
    return data

# Generate 5 real numbers rounded to 3 decimal places
real_numbers = [round(random.random() * 100, 3) for _ in range(5)]

# Generate 2 integers between 0 and 100
integers = [random.randint(0, 100) for _ in range(2)]

# Create the dictionary with the specified structure
data = {
    "P": real_numbers[0],
    "Q": real_numbers[1],
    "V": real_numbers[2],
    "f": real_numbers[3],
    "angle": real_numbers[4],
    "status": integers[0],
    "mode": integers[1]
}

# Save the data to a JSON file
file_name = 'PowerGridData.json'
with open(file_name, 'w') as json_file:
    json.dump(data, json_file, indent=4)

print(f"JSON file '{file_name}' created successfully.")
