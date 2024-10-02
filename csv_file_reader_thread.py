import csv, random, os, time, threading, subprocess 

# The following method reads the power_grid_input.csv file and returns any new information that has been added to it
def read_csv_file(file_path, last_row_count):
    # Initialize an empty list to store new rows
    new_rows = []

    # Check if the file exists
    if os.path.exists(file_path):
        with open(file_path, mode='r', newline='') as file:
            reader = csv.reader(file)
            all_rows = list(reader)

            # If there are more rows than the last recorded count, there are new rows
            current_row_count = len(all_rows)
            if current_row_count > last_row_count:
                new_rows = all_rows[last_row_count:]  # Get only new rows
                return new_rows, current_row_count

    return [], last_row_count

# The following method periodically uses the read_csv_file method to see if any new information has been added to the power_grid_input.csv file 
def monitor_csv_file(interval=5):
    # Initialize the last row count to 0 (assuming no rows initially)
    last_row_count = 0

    while True:
        # Check the CSV file for new rows
        csv_file_path = './power_grid_datafiles/power_grid_input.csv'
        new_rows, last_row_count = read_csv_file(csv_file_path, last_row_count)

        # If there are new rows, print them
        if new_rows:
            print("New rows added:")
            for row in new_rows:
                print(row)

        # Wait for the specified interval before checking again
        time.sleep(interval)

# The following method enables threading of the csv file monitoring and allows for shell commands while the main program is running
def run_shell_command(command):
    try:
        # Use subprocess to run the command from the terminal
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(result.stdout.decode())  # Print the command output
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e.stderr.decode()}")


