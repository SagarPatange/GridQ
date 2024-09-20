import csv
import json

# Define the path to the CSV file and the output JSON file
csv_file_path = 'input.csv'
json_file_path = 'output.json'

# Function to convert CSV data to JSON
def convert_csv_to_json(csv_file_path, json_file_path):
    # Open the CSV file for reading
    with open(csv_file_path, mode='r', newline='') as csv_file:
        # Create a CSV reader object using DictReader, which directly reads each row to a dictionary
        csv_reader = csv.DictReader(csv_file)
        
        # Convert csv_reader to a list of dictionaries (one dictionary per row)
        data = list(csv_reader)

    # Open the JSON file for writing
    with open(json_file_path, mode='w') as json_file:
        # Dump the list of dictionaries to the JSON file
        # `indent=4` is used for pretty printing the JSON data
        json.dump(data, json_file, indent=4)
    
    print(f"CSV data has been successfully converted to JSON and saved in '{json_file_path}'")

# Call the function to convert CSV to JSON
convert_csv_to_json(csv_file_path, json_file_path)
