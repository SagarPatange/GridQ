import json

# List of values
values = ['23:12:02', '78.341', '37.447', '12.191', '30.998', '14.05', '', '', '']

# Dictionary with metadata keys
keys = ["real_time_sent", "P", "Q", "V", "f", "angle", "real_time_recieved", "real_time_elapsed", "estimated_end-to-end_real_time"]

# Combine keys and values into a dictionary
data_dict = dict(zip(keys, values))

# Convert dictionary back to JSON string
data_string = json.dumps(data_dict)

# Display the string
data_string