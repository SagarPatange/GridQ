from queue import Queue
import time, csv, os
from message_application_components.power_grid_csv_generator import write_input_to_powergrid_csv_file


# Function to monitor the CSV file for new data and add it to the queue

def monitor_csv_file_row(file_path: str, interval: float, q: Queue):
    last_line_count = 1

    while True:
        time.sleep(interval)  # Wait for the interval time
        try:
            with open(file_path, mode='r') as file:
                csv_reader = list(csv.reader(file))
                current_line_count = len(csv_reader)

                # If new rows have been added, check each new row
                if current_line_count > last_line_count:
                    for i in range(last_line_count, current_line_count):
                        # Check if all values in the row are filled (non-empty)
                        if all(cell.strip() for cell in csv_reader[i]):
                            q.put(csv_reader[i])  # Add the fully filled row to the queue

                    last_line_count = current_line_count  # Update the last known line count

        except FileNotFoundError:
            print(f"File not found: {file_path}")
            continue

def monitor_csv_file(file_path: str, interval: float, q: Queue):
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
    Gracefully handles non-interactive environments (e.g., Docker without -it).
    """
    # Calculate path to power_grid_datafiles relative to this script
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = os.path.join(script_dir, 'power_grid_datafiles', 'power_grid_input.csv')

    try:
        while True:
            user_command = input()

            if user_command.lower() == 'exit':
                print("Exiting the program.")
                os._exit(0)
            if user_command.lower() == 'generate data':
                write_input_to_powergrid_csv_file(csv_path)
    except EOFError:
        # No stdin available (e.g., Docker without -it flag)
        # Silently exit the user input thread
        pass

