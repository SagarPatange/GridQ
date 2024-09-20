import csv
import random

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
