import threading, queue, time, csv, random, os
from datetime import datetime
from message_application_components.power_grid_csv_generator import write_input_to_powergrid_csv_file


# Function to monitor the CSV file for new data and add it to the queue
def monitor_csv_file(file_path, interval, q):
    last_line_count = 1

    while True:
        time.sleep(interval)  # Wait for the interval time
        try:
            with open(file_path, mode='r') as file:
                csv_reader = list(csv.reader(file))
                current_line_count = len(csv_reader)

                # If new rows have been added, put them in the queue
                if current_line_count > last_line_count:
                    last_line_count = current_line_count  # Update the last known line count
                    q.put(last_line_count)  # Add each new row to the queue

        except FileNotFoundError:
            print(f"File not found: {file_path}")
            continue

def user_input():
    """
    Handles user input in a separate thread.
    """
    while True:
        user_command = input()

        if user_command.lower() == 'exit':
            print("Exiting the program.")
            os._exit(0)
        if user_command.lower() == 'generate data':
            write_input_to_powergrid_csv_file()

