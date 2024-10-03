import csv
import random
import os  
import json
from datetime import datetime

import csv
import random
import os

# import csv
import random
import os

def write_input_to_powergrid_csv_file(current_time, csv_file_path='./power_grid_datafiles/power_grid_input.csv'):
    # Predefined headers
    required_headers = ["Time", "P", "Q", "V", "f", "angle", "status", "mode"]

    # Generate 5 real numbers rounded to 3 decimal places
    real_numbers = [round(random.random() * 100, 3) for _ in range(5)]

    # Generate 2 integers between 0 and 100
    integers = [random.randint(0, 100) for _ in range(2)]

    # Create the dictionary with the specified structure
    data = {
        "Time": current_time,
        "P": real_numbers[0],
        "Q": real_numbers[1],
        "V": real_numbers[2],
        "f": real_numbers[3],
        "angle": real_numbers[4],
        "status": integers[0],
        "mode": integers[1]
    }

    # Check if the file exists
    file_exists = os.path.exists(csv_file_path)
    
    # Read existing content if the file exists
    existing_data = []
    if file_exists:
        with open(csv_file_path, mode='r', newline='') as file:
            csv_reader = csv.reader(file)
            existing_data = list(csv_reader)  # Read all existing data

    # Open the file in write mode ('w') to overwrite it
    with open(csv_file_path, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=required_headers)

        # Write the required headers at the top
        writer.writeheader()

        # Write existing data (if any), ignoring the previous headers
        if file_exists and len(existing_data) > 1:  # If there is more than just the header
            for row in existing_data[1:]:  # Skip the previous header
                file.write(','.join(row) + '\n')

        # Write the new data row
        writer.writerow(data)

    print(f"Data has been written to '{csv_file_path}'")


def erase_powergrid_csv_data(csv_file_path = './power_grid_datafiles/power_grid_input.csv'):
    # Read the headers from the file
    with open(csv_file_path, mode='r') as file:
        reader = csv.reader(file)
        headers = next(reader)  # Get the first row (headers)

    # Rewrite the file, keeping only the headers
    with open(csv_file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(headers)  # Write the headers back to the file

    print(f"Data deleted in '{csv_file_path}'.")

def csv_to_string (csv_file_path):  

    '''
    Method converts CSV to JSON, then converts JSON to string

    returns: a string of data in csv file 
    '''

    json_file_path = './power_grid_datafiles/power_grid_input.json'
    with open(csv_file_path, mode='r', newline='') as csv_file:
        csv_reader = csv.DictReader(csv_file) # Create a CSV reader object using DictReader, which directly reads each row to a dictionary
        data = list(csv_reader) # Convert csv_reader to a list of dictionaries (one dictionary per row)

    # Open the JSON file for writing
    with open(json_file_path, mode='w') as json_file:
        json.dump(data, json_file, indent=4)
    
    # print(f"CSV data has been successfully converted to JSON and saved in '{json_file_path}'")
    with open(json_file_path, 'r') as f:
        json_data = json.load(f)
    json_string = [json.dumps(json_data)]

    return json_string
        
def string_to_csv (data_string):  

    '''
    Method converts string to JSON, then converts JSON to CSV

    '''

    data = json.loads(data_string)

    # Define the path to the output JSON file
    json_file_path = './power_grid_datafiles/power_grid_output.json'
    csv_file_path = './power_grid_datafiles/power_grid_output.csv'
    # Write the Python object to a JSON file
    with open(json_file_path, 'w') as json_file:
        # Write the data to the file; indent=4 for pretty-printing
        json.dump(data, json_file, indent=4)

    with open(json_file_path, 'r') as json_file:
        # Load the entire JSON content into a Python list (assuming it's an array of objects)
        data = json.load(json_file)

    # Open the CSV file for writing
    with open(csv_file_path, mode='w', newline='') as csv_file:
        # Assuming that all dictionaries in 'data' have the same keys
        if data:
            # Extract headers (keys) from the first item (this assumes that all dicts have the same keys)
            headers = data[0].keys()

            # Create a CSV writer object and write the header row
            csv_writer = csv.DictWriter(csv_file, fieldnames=headers)
            csv_writer.writeheader()

            # Write the data rows
            csv_writer.writerows(data)
    

def save_data_to_csv(output_csv_path, data_row):
    """
    Appends the data row (without metadata) to the output CSV file.
    """
    try:
        # Open the output CSV in append mode to add new rows
        with open(output_csv_path, mode='a', newline='') as file:
            writer = csv.writer(file)
            # Write only the data row to the output CSV
            writer.writerow(data_row)
        print(f"Data saved to {output_csv_path}")
    except Exception as e:
        print(f"Error writing to file: {e}")
        
def append_json_to_csv(csv_file_path, json_string):
    """
    Converts a JSON string to a row in an existing CSV file.
    The JSON string contains the metadata (headings) and the data.
    """
    try:
        # Parse the JSON string into a dictionary
        data_dict = json.loads(json_string)

        # Read the existing CSV file to check for headers
        with open(csv_file_path, mode='r', newline='') as file:
            csv_reader = csv.reader(file)
            headers = next(csv_reader)  # Extract existing CSV headers

        # Ensure the keys in the JSON match the headers in the CSV
        if set(data_dict.keys()) != set(headers):
            print("The JSON keys do not match the CSV headers.")
            return

        # Append the data to the CSV file
        with open(csv_file_path, mode='a', newline='') as file:
            csv_writer = csv.DictWriter(file, fieldnames=headers)
            # Write the data from the JSON string
            csv_writer.writerow(data_dict)
        print("Data successfully added to the CSV file.")

    except FileNotFoundError:
        print(f"File not found: {csv_file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")



def read_csv_nth_row(csv_file_path, n):
    """
    Reads the nth row from the CSV file and returns a JSON string
    with metadata as keys and data as values.
    """
    try:
        with open(csv_file_path, mode='r') as file:
            csv_reader = csv.reader(file)
            # Extract the first row (headings)
            headings = next(csv_reader)
            
            # Find the nth row
            for current_row_index, row in enumerate(csv_reader, start=1):
                if current_row_index == n:
                    # Create a dictionary combining metadata and data
                    row_data = {headings[i]: row[i] for i in range(len(headings))}
                    # Convert the dictionary to a JSON string
                    json_data = json.dumps(row_data, separators=(',', ':'))
                    return json_data
        return None  # If nth row does not exist
    except FileNotFoundError:
        print(f"File not found: {csv_file_path}")
        return None



if __name__ == "__main__":
    # erase_powergrid_csv_data('./power_grid_datafiles/power_grid_output.csv')
    # current_time = datetime.now().strftime("%H:%M:%S")
    # write_input_to_powergrid_csv_file(current_time, './power_grid_datafiles/power_grid_output.csv')    
    pass