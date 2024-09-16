'''
This file is used to develop an encryption method that is suitable for quantum communication system. 
The file starts with easier to break encryption methods that were used earlier in development to harder encruption methods. 

Encryption method list:
1. Ceaser Shift One Time Pad - scrambles the alphabet by a shift factor. 
2. ChatGPT implemented one time pad - not sure on how it works. 

'''

''' Text to binary and Vice Versa'''

def text_to_binary(text):
    binary_result = ' '.join(format(ord(char), '08b') for char in text)
    return binary_result
def binary_to_text(binary_string):
    binary_values = binary_string.split()
    ascii_characters = [chr(int(bv, 2)) for bv in binary_values]
    text_result = ''.join(ascii_characters)
    return text_result

# Example usage - run this function in __main__:
def test_b_to_t():
    cipher = onetimepad.encrypt('Some text', 'a_random_key')
    print(cipher)
    binary_message = text_to_binary(cipher)
    print(binary_message)
    cipher = binary_to_text(binary_message)
    print(cipher)
    msg = onetimepad.decrypt(cipher, 'a_random_key')
    print(msg)

''' Encryption method 1: Chat-GPT one-time-pad '''

def otp_encrypt(plaintext, key):
    """
    Method to encrypt a message given a key 

    Parameters:
    plaintext (String): the message that needs encrypting
    key (int): the key that the message needs to be encrypted with 
    """
    key_string = str(key)
    if len(plaintext) != len(key_string):
        if len(key_string) > len(plaintext):
            key_string = key_string[len(key_string) - len(plaintext):]  
    encrypted_message = ''.join(chr(ord(p) ^ ord(k)) for p, k in zip(plaintext, key_string))
    return encrypted_message

def otp_decrypt(ciphertext, key):
    """
    Method to decrypt a message given a key 

    Parameters:
    ciphertext (String): the message that needs decrypting
    key (int): the key that the message needs to be decrypted with 
    """
    key_string = str(key)
    if len(ciphertext) != len(key_string):
        if len(key_string) > len(ciphertext):
            key_string = key_string[len(key_string) - len(ciphertext):]
    decrypted_message = ''.join(chr(ord(c) ^ ord(k)) for c, k in zip(ciphertext, key_string))
    return decrypted_message
    
''' Encryption method 2: uses the onetimepad package from python '''

import onetimepad

# Plain text that you want to encrypt
def test_onetimepad():
    plaintext = 'hello world'

    # Encrypting the text using a random key
    ciphertext = onetimepad.encrypt(plaintext, 'randomkey')
    print('Encrypted:', ciphertext)    
    decrypted_text = onetimepad.decrypt(ciphertext, 'randomkey')
    print('Decrypted:', decrypted_text) 

if __name__ == "__main__" :

    pass