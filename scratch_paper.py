import threading
import collections
import time

# Shared deque to communicate between main thread and worker thread
command_queue = collections.deque()

# Worker thread that monitors the deque
def worker():
    variable = 0  # Initial value of the variable
    print(f"Initial variable value: {variable}")
    while True:
        # Check for new commands if there are items in the deque
        if command_queue:
            # Peek at the first element without removing it
            command = command_queue[0]
            if command == "quit":
                print("Exiting thread...")
                break
            elif command.startswith("set "):
                # Parse the new value after 'set '
                try:
                    new_value = int(command.split()[1])
                    variable = new_value
                    print(f"Variable updated to: {variable}")
                except ValueError:
                    print("Invalid input: Please enter a valid integer.")
                # Remove the command after processing
                command_queue.popleft()
            else:
                print("Unknown command. Use 'set <number>', 'update <number>' or 'quit' to exit.")
                command_queue.popleft()
        time.sleep(1)

# Start the worker thread
worker_thread = threading.Thread(target=worker)
worker_thread.start()

# Main thread: Get commands from the user and put them in the deque
try:
    while True:
        command = input("Enter command (set <number>, update <number> or quit): ")
        
        if command.startswith("update "):
            # Update the first element in the queue without removing it
            if command_queue:
                # Modify the first command
                command_queue[0] = command
                print(f"First element of the queue updated to: {command}")
            else:
                print("Queue is empty. Nothing to update.")
        else:
            # Add command to the queue normally
            command_queue.append(command)

        if command == "quit":
            break
except KeyboardInterrupt:
    print("\nKeyboard interrupt received. Exiting...")

# Wait for the worker thread to finish
worker_thread.join()
print("Program terminated.")
