import numpy as np
import matplotlib.pyplot as plt 
from colorama import Fore, Style, init
init()   


# result_list_change = []
    # result_list_noChange = []
    # for i in range(10):
    #     results = test(sim_time = 1000, msg = strings_list, internode_distance= 1e3, 
    #         attenuation = 1e-5, polarization_fidelity = 0.97, eavesdropper_eff = 0.0, backup_qc = True)
    #     result_list_change.append(results)
    # for i in range(10):
    #     results = test(sim_time = 1000, msg = strings_list, internode_distance= 1e3, 
    #         attenuation = 1e-5, polarization_fidelity = 0.97, eavesdropper_eff = 0.0, backup_qc = False)
    #     result_list_noChange.append(results)

    # x1 = np.full(10, 1)
    # x2 = np.full(10, 2)

    # plt.scatter(x1, result_list_change, color = 'b')
    # plt.scatter(x2, result_list_noChange, color = 'r')

    # plt.xticks([1, 2], ['Change', 'No Change'])

    # # Add space before the first tick by adjusting xlim (left side)
    # plt.xlim(0, 3)
    # #plt.xlim(2.5, 3)  
    # # Add titles and labels
    # plt.title("Quantum Channel time - Change vs No Change")
    # plt.xlabel("Change vs no Change")
    # plt.ylabel("End to end time (ms)")

    # # Show the plot
    # plt.show()



# Initialize colorama


def compare_and_print_lists(list1, list2):
    max_len = max(len(list1), len(list2))
    
    # Extend both lists to the maximum length by appending empty strings
    list1.extend([''] * (max_len - len(list1)))
    list2.extend([''] * (max_len - len(list2)))

    # Compare and print the lists with mismatched elements in red
    error_counter = 0
    total_string_length = 0
    letter_differences = 0
    for item1, item2 in zip(list1, list2):
        if item1 != item2:
            print(f"{Fore.RED}{item1}{Style.RESET_ALL}" if item1 else "", end=' ')
            print(f"{Fore.RED}{item2}{Style.RESET_ALL}" if item2 else "")
            error_counter +=1
            total_string_length += len(item1)
            letter_differences += count_character_differences(item1, item2)
        else:
            print(item1, item2)
            total_string_length += len(item1)
    
    return error_counter/len(list1), letter_differences/total_string_length

def count_character_differences(str1, str2):
    max_len = max(len(str1), len(str2))
    str1 = str1.ljust(max_len)
    str2 = str2.ljust(max_len)
    differences = sum(1 for c1, c2 in zip(str1, str2) if c1 != c2)  
    return differences


# Function to compare two strings and print mismatched letters in red
def compare_strings_with_color(string1, string2):
    # ANSI escape code for red text
    RED_START = '\033[91m'
    RED_END = '\033[0m'

    result1 = []
    result2 = []
    difference_count = 0

    # Iterate through both strings character by character
    for ch1, ch2 in zip(string1, string2):
        if ch1 == ch2:
            # If characters match, append normally
            result1.append(ch1)
            result2.append(ch2)
        else:
            # If characters don't match, append with red color and increase difference count
            result1.append(f"{RED_START}{ch1}{RED_END}")
            result2.append(f"{RED_START}{ch2}{RED_END}")
            difference_count += 1

    # Calculate error percentage
    error_percentage = (difference_count / len(string1)) * 100 if string1 else 0

    # Join the results and print them
    print("Sender's (Alice) message:", ''.join(result1))
    print("Receiver's (Bob) message:", ''.join(result2))
    print(f"Character Differences: {difference_count}")
    print(f"Error Percentage: {error_percentage:.2f}%")

def test_compare_strings():
    # Example usage
    string1 = "Hello, World!"
    string2 = "Hella, Wardd!"

    # Call the function to compare and print the strings with color
    compare_strings_with_color(string1, string2)

if __name__ == '__main__':
    pass
