import csv
import random
import os  
import json
from datetime import datetime

def generate_input_data(filename = "./power_grid_datafiles/power_grid_input.csv"):
    real_numbers = [round(random.random() * 100, 3) for _ in range(5)]
    required_headers = ["P", "Q", "V", "f", "angle"]
    data = {
        "P": real_numbers[0],
        "Q": real_numbers[1],
        "V": real_numbers[2],
        "f": real_numbers[3],
        "angle": real_numbers[4]
    }

    with open(filename, mode="a", newline = filename) as file:
        writer = csv.DictWriter(file, fieldnames=required_headers)
        
        # Check if the file is empty to write the header only once
        if file.tell() == 0:
            writer.writeheader()  # Write the header if the file is new or empty
    
        writer.writerow(data)  # Append the row of data

def write_input_to_powergrid_csv_file(csv_file_path='./power_grid_datafiles/power_grid_input.csv'):
    required_headers = ["P", "Q", "V", "f", "angle"]
    real_numbers = [round(random.random() * 100, 3) for _ in range(5)]
    data = {
        "P": real_numbers[0],
        "Q": real_numbers[1],
        "V": real_numbers[2],
        "f": real_numbers[3],
        "angle": real_numbers[4],
    }

    file_exists = os.path.exists(csv_file_path)
    existing_data = []
    if file_exists:
        with open(csv_file_path, mode='r', newline='') as file:
            csv_reader = csv.reader(file)
            existing_data = list(csv_reader)  # Read all existing data
    with open(csv_file_path, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=required_headers)
        writer.writeheader()

        # Write existing data (if any), ignoring the previous headers
        if file_exists and len(existing_data) > 1:  # If there is more than just the header
            for row in existing_data[1:]:  # Skip the previous header
                file.write(','.join(row) + '\n')

        # Write the new data row
        writer.writerow(data)

    # print(f"Data has been written to '{csv_file_path}'")


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

def write_output_data(json_string, end_to_end_sim_time, csv_file_path = './power_grid_datafiles/power_grid_output.csv'):
    data_dict = json.loads(json_string)
    data_dict['simulation_time'] = end_to_end_sim_time

    try:
        with open(csv_file_path, mode='r+', newline='') as file:
            reader = csv.reader(file)
            existing_headers = next(reader, None)

            # Check if headers need to be replaced
            if existing_headers != list(data_dict.keys()):
                # Move to the beginning and overwrite with new headers and existing data
                file.seek(0)
                writer = csv.DictWriter(file, fieldnames=data_dict.keys())
                writer.writeheader()

                # Re-write existing rows with new headers if they are present
                for row in reader:
                    writer.writerow(dict(zip(existing_headers, row)))
                
            # Move to the end of the file to append the new row
            writer = csv.DictWriter(file, fieldnames=data_dict.keys())
            writer.writerow(data_dict)

    except FileNotFoundError:
        # If file does not exist, create it and write the data
        with open(csv_file_path, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=data_dict.keys())
            writer.writeheader()
            writer.writerow(data_dict)
            
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
        # print("Data successfully added to the CSV file.")

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
    erase_powergrid_csv_data('./power_grid_datafiles/power_grid_input.csv')
    # current_time = datetime.now().strftime("%H:%M:%S")
    write_input_to_powergrid_csv_file('./power_grid_datafiles/power_grid_input.csv')    
    pass