import threading, queue, time, csv, random, os
from datetime import datetime
from message_application_components.power_grid_csv_generator import write_input_to_powergrid_csv_file


# Function to monitor the CSV file for new data and add it to the queue
def monitor_csv_file(file_path, interval, q):
    last_line_count = 0

    while True:
        time.sleep(interval)  # Wait for the interval time
        try:
            with open(file_path, mode='r') as file:
                csv_reader = list(csv.reader(file))
                current_line_count = len(csv_reader)

                # If new rows have been added, put them in the queue
                if current_line_count > last_line_count:
                    new_rows = csv_reader[last_line_count:]  # Get only new rows
                    last_line_count = current_line_count  # Update the last known line count
                    q.put(last_line_count)  # Add each new row to the queue

        except FileNotFoundError:
            print(f"File not found: {file_path}")
            continue

# Function to simulate running shell commands
def run_shell_command(command):
    print(f"Running command: {command}")

def user_input():
    """
    Handles user input in a separate thread.
    """
    while True:
        # Allow the user to input terminal commands
        user_command = input("Enter a command (type 'exit' to quit and 'generate data' to add data to power_grid_input.csv): ")

        if user_command.lower() == 'exit':
            print("Exiting the program.")
            os._exit(0)
        if user_command.lower() == 'generate data':
            current_time = datetime.now().strftime("%H:%M:%S")
            write_input_to_powergrid_csv_file(current_time)

        # Start a new thread to execute the user command without blocking the loop
        command_thread = threading.Thread(target=run_shell_command, args=(user_command,))
        command_thread.start()
