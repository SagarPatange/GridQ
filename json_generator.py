import json
import random
import string

def generate_random_string(length):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def generate_list_of_strings(num_strings):
    return [generate_random_string(random.randint(5, 10)) for _ in range(num_strings)]

def save_to_json(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

# Specify the number of strings you want to generate
num_strings = 50  # Change this number as needed

# Generate the list of strings
random_strings = generate_list_of_strings(num_strings)

# Save the list to a JSON file
filename = 'random_strings.json'
save_to_json(random_strings, filename)

print(f"{num_strings} random strings saved to '{filename}'")

