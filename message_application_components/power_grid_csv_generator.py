import csv
import random
import json 

def write_input_powergrid_csv_file():
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

    # Path to the CSV file where data will be written
    csv_file_path = './power_grid_datafiles/power_grid_input.csv'

    # Open the CSV file for writing
    with open(csv_file_path, mode='w', newline='') as file:
        # Create a CSV writer object
        writer = csv.DictWriter(file, fieldnames=data.keys())
        
        # Write the header (field names)
        writer.writeheader()
        
        # Write the data dictionary as a row in the CSV
        writer.writerow(data)

    print(f"Data has been written to '{csv_file_path}'")

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
    