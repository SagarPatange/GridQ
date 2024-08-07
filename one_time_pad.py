#!/usr/bin/env python3

import onetimepad

def text_to_binary(text):
    binary_result = ' '.join(format(ord(char), '08b') for char in text)
    return binary_result
def binary_to_text(binary_string):
    binary_values = binary_string.split()
    ascii_characters = [chr(int(bv, 2)) for bv in binary_values]
    text_result = ''.join(ascii_characters)
    return text_result

# Example usage:

print("############################################################")
cipher = onetimepad.encrypt('Some text', 'a_random_key')
print(cipher)
binary_message = text_to_binary(cipher)
print(binary_message)
cipher = binary_to_text(binary_message)
print(cipher)
msg = onetimepad.decrypt(cipher, 'a_random_key')
print(msg)

