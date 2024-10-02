import csv
import random
import os  
import time
import threading
import subprocess


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

        print('main pr')

# Path to the CSV file

# # Call the function to start monitoring the CSV file for new rows
# monitor_csv_file(csv_file_path, interval=5)  # Check every 5 seconds

def run_shell_command(command):
    try:
        # Use subprocess to run the command from the terminal
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(result.stdout.decode())  # Print the command output
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e.stderr.decode()}")

if __name__ == "__main__":
    # Create and start a thread for the forever loop
    forever_loop_thread = threading.Thread(target=monitor_csv_file)
    forever_loop_thread.daemon = True  # Daemon thread exits when the main program exits
    forever_loop_thread.start()

    # Run the interactive command input in the main thread
    while True:
        # Allow the user to input terminal commands
        user_command = input("Enter a command to run (type 'exit' to quit): ")

        if user_command.lower() == 'exit':
            print("Exiting the program.")
            break

        # Start a new thread to execute the user command without blocking the loop
        command_thread = threading.Thread(target=run_shell_command, args=(user_command,))
        command_thread.start()
