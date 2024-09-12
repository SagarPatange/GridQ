# Function to compare two strings and print mismatched letters in red
def compare_strings_with_color(string1, string2):
    # ANSI escape code for red text
    RED_START = '\033[91m'
    RED_END = '\033[0m'

    result1 = []
    result2 = []

    # Iterate through both strings character by character
    for ch1, ch2 in zip(string1, string2):
        if ch1 == ch2:
            # If characters match, append normally
            result1.append(ch1)
            result2.append(ch2)
        else:
            # If characters don't match, append with red color
            result1.append(f"{RED_START}{ch1}{RED_END}")
            result2.append(f"{RED_START}{ch2}{RED_END}")

    # Join the results and print them
    print("String 1:", ''.join(result1))
    print("String 2:", ''.join(result2))

# Example usage
string1 = "Hello, World!"
string2 = "Hella, Wardd!"

# Call the function to compare and print the strings with color
compare_strings_with_color(string1, string2)
