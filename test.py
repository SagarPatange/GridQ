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
    
    
