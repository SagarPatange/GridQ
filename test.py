import csv
import json

def append_json_to_csv(json_string, csv_file_path):
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

# Example usage
json_string = """
{
    "Name": "Charlie",
    "Age": "35",
    "City": "Los Angeles"
}
"""
csv_file_path = 'example.csv'

append_json_to_csv(json_string, csv_file_path)
