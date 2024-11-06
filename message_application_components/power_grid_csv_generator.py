import csv
import random
import os  
import json
from datetime import datetime


def write_input_to_powergrid_csv_file(csv_file_path='./power_grid_datafiles/power_grid_input.csv'):
    # Predefined headers
    required_headers = ["P", "Q", "V", "f", "angle", "simulation_time"]

    # Generate 5 real numbers rounded to 3 decimal places
    real_numbers = [round(random.random() * 100, 3) for _ in range(5)]

    # Generate 2 integers between 0 and 100
    # integers = [random.randint(0, 100) for _ in range(2)]

    # Create the dictionary with the specified structure
    data = {
        "P": real_numbers[0],
        "Q": real_numbers[1],
        "V": real_numbers[2],
        "f": real_numbers[3],
        "angle": real_numbers[4],
        "simulation_time": None
        # "status": integers[0],
        # "mode": integers[1]
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
        
def append_json_to_csv(csv_file_path, json_string, end_to_end_sim_time):
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
        
        # Add the current time and time difference to the dictionary
        data_dict['simulation_time'] = end_to_end_sim_time
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

def data_to_metastring (values):

    keys = ["P", "Q", "V", "f", "angle", "simulation_time"]
    data_dict = dict(zip(keys, values))
    data_string = json.dumps(data_dict)
    return data_string

if __name__ == "__main__":
    erase_powergrid_csv_data('./power_grid_datafiles/power_grid_output.csv')
    # current_time = datetime.now().strftime("%H:%M:%S")
    write_input_to_powergrid_csv_file('./power_grid_datafiles/power_grid_output.csv')    
    pass