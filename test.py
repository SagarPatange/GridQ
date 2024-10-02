import threading
import time
import queue

# Function that will run in a separate thread
def threaded_function(output_queue, data):
    time.sleep(2)  # Simulating some work
    result = data * 2  # Example result of a computation
    output_queue.put(result)  # Put the result into the queue

# Main code
if __name__ == "__main__":
    q = queue.Queue()  # Create a Queue to store the result
    
    # Create and start the thread, passing the queue and some data
    thread = threading.Thread(target=threaded_function, args=(q, 5))
    thread.start()

    # Wait for the thread to finish
    thread.join()

    # Retrieve the result from the queue
    result = q.get()
    print("Thread result:", result)
