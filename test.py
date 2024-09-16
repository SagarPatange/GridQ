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
    print("String 1:", ''.join(result1))
    print("String 2:", ''.join(result2))
    print(f"Character Differences: {difference_count}")
    print(f"Error Percentage: {error_percentage:.2f}%")

# Example usage:
compare_strings_with_color("hello world", "he11o wor1d")
