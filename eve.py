import random


class Alice():
    
    def __init__(self):
        self.random_bits = []
        self.random_bases = []
        self.encoded_bits = []   
        self.sent_to_bob = False
        self.eavedropped = False

    def generate_random_bits(self, n):
    """
    Generates a random bit sequence of length n.
    
    Parameters:
    n (int): The length of the bit sequence to generate.
    
    Returns:
    list: A list containing the random bit sequence.
    """
        self.random_bits = [random.randint(0, 1) for _ in range(n)]

    def generate_random_bases(self, n):
    """
    Generates a random sequence of bases (0 for rectilinear, 1 for diagonal) of length n.
    
    Parameters:
    n (int): The length of the bases sequence to generate.
    
    Returns:
    list: A list containing the random bases sequence.
    """
        self.random_bases = [random.choice(['H', 'V']) for _ in range(n)]

    def encode_bits(self, bits, bases):
    """
    Generates an encoded array of bits which will be in the H base of the V base.
    
    Parameters:
    bits (array): array of random bits 0 or 1
    bases (array): array of random bases "H" or "V"
    
    Returns:
    Array: array containing "Up", "Down", "Left", or "Right"
    """
        # Encodes the bits using the given bases
        encoded_qubits = []
        for i in range(len(bits)):
            if bases[i] == 'H':
                if bits[i] == 0:
                    encoded_qubits.append("Up")
                else:
                    encoded_qubits.append("Down")
            else:
                if bits[i] == 0:
                    encoded_qubits.append("Left")
                else:
                    encoded_qubits.append("Right")
        self.encoded_bits = encoded_qubits

    def send_qubits_to_bob(self, bob, eve = None):

        if self.eavedropped:
            eve.eavesdropper(self.random_bases)
        bob.recieve_bits(self.encoded_bits)
        self.sent_to_bob = True
        
    def show_encoded_bits(self):
        return self.encoded_bits
    
    def eve_present(self):
        self.eavedropped = True


class Eve ():
    def __init__(self):
        self.random_bases = []
        self.recieved_message = []
        self.decoded_message = []

    def generate_random_bases(self, n):
        """
        Generates a random sequence of bases (0 for rectilinear, 1 for diagonal) of length n.
        
        Parameters:
        n (int): The length of the bases sequence to generate.
        
        Returns:
        list: A list containing the random bases sequence.
        """
        self.random_bases = [random.choice(['H', 'V']) for _ in range(n)]

    def eavesdropper (self, alice_random_base):
        encoded_message = self.recieved_message
        decoded_message = []
        for i in range(len(alice_random_base)):
            if random_base[i] == 'H':
                if self.recieved_message[i] == 'Up'
                    decoded_message.append(0)
                if self.recieved_message[i] == 'Down'
                    decoded_message.append(1)
                if self.recieved_message[i] == 'Left'
                    decoded_message.append(random.randint(0,1))
                if self.recieved_message[i] == 'Right'
                    decoded_message.append(random.randint(0,1))
            if alice_random_base[i] == 'V':
                if self.recieved_message[i] == 'Up'
                    decoded_message.append(random.randint(0,1))
                if self.recieved_message[i] == 'Down'
                    decoded_message.append(random.randint(0,1))
                if self.recieved_message[i] == 'Left'
                    decoded_message.append(0)
                if self.recieved_message[i] == 'Right'
                    decoded_message.append(1)
        self.decoded_message = decoded.message



class Bob():
    def __init__(self):
            self.recieved_message = []
            self.random_bases = []

    def recieve_bits(self, alice):
        self.recieved_message = alice.show_encoded_bits()

    def generate_random_bases(self, n):
        """
        Generates a random sequence of bases (0 for rectilinear, 1 for diagonal) of length n.
        
        Parameters:
        n (int): The length of the bases sequence to generate.
        
        Returns:
        list: A list containing the random bases sequence.
        """
        self.random_bases = [random.choice(['H', 'V']) for _ in range(n)]
    
    def decode_alice_message (self, random_base):
        encoded_message = self.recieved_message
        decoded_message = []
        for i in range(len(random_base)):
            if random_base[i] == 'H':
                if self.recieved_message[i] == 'Up'
                    decoded_message.append(0)
                if self.recieved_message[i] == 'Down'
                    decoded_message.append(1)
                if self.recieved_message[i] == 'Left'
                    decoded_message.append(None)
                if self.recieved_message[i] == 'Left'
                    decoded_message.append(None)
            if random_base[i] == 'V':
                if self.recieved_message[i] == 'Up'
                    decoded_message.append(None)
                if self.recieved_message[i] == 'Down'
                    decoded_message.append(None)
                if self.recieved_message[i] == 'Left'
                    decoded_message.append(0)
                if self.recieved_message[i] == 'Right'
                    decoded_message.append(1)
        self.decoded_message = decoded.message


# Step 1: Alice generates a random bit sequence
alice_bits = generate_random_bits(10)

# Step 2: Alice generates a random sequence of bases
alice_bases = generate_random_bases(10)

# Step 3: Alice encodes bits using the bases
encoded_qubits = encode_bits(alice_bits, alice_bases)

# Step 4: Alice sends encoded qubits to Bob through quantum channel
send_qubits_to_bob(encoded_qubits)

# Step 5: Eve intercepts the qubits
intercepted_qubits = intercept_qubits(encoded_qubits)

# Step 6: Eve generates a random sequence of bases and measures the qubits
eve_bases = generate_random_bases(n)
eve_bits = measure_qubits(intercepted_qubits, eve_bases)

# Step 7: Eve re-encodes and sends the qubits to Bob
reencoded_qubits = encode_bits(eve_bits, eve_bases)
send_qubits_to_bob(reencoded_qubits)

# Step 8: Bob generates a random sequence of bases
bob_bases = generate_random_bases(n)

# Step 9: Bob measures received qubits using his bases
bob_bits = measure_qubits(reencoded_qubits, bob_bases)

# Step 10: Alice and Bob publicly share their bases
public_share(alice_bases, bob_bases)

# Step 11: Alice and Bob compare their bases
matching_indices = find_matching_bases(alice_bases, bob_bases)

# Step 12: Alice and Bob discard bits where bases don't match
alice_key = extract_bits(alice_bits, matching_indices)
bob_key = extract_bits(bob_bits, matching_indices)

# Step 13: Alice and Bob publicly share a subset of their keys to check for eavesdropping
alice_sample = sample_bits(alice_key)
bob_sample = sample_bits(bob_key)

# Step 14: Compare the samples
if (alice_sample == bob_sample) {
    // No eavesdropping detected
    final_key = alice_key // or bob_key, since they should be identical
} else {
    // Eavesdropping detected, abort the protocol
    abort_protocol()
}





def measure_qubits(qubits, bases):
    # Measures the qubits using the given bases
    measured_bits = []
    for i in range(len(qubits)):
        if bases[i] == 0:
            measured_bits.append(measure_rectilinear(qubits[i]))
        else:
            measured_bits.append(measure_diagonal(qubits[i]))
    return measured_bits

# def find_matching_bases(alice_bases, bob_bases):
#     // Finds the indices where Alice's and Bob's bases match
#     matching_indices = []
#     for i in range(len(alice_bases)):
#         if alice_bases[i] == bob_bases[i]:
#             matching_indices.append(i)
#     return matching_indices

# def extract_bits(bits, indices):
#     // Extracts bits from the given indices
#     extracted_bits = []
#     for index in indices:
#         extracted_bits.append(bits[index])
#     return extracted_bits

# def sample_bits(bits):
#     // Samples a subset of the bits for eavesdropping check
#     return random_sample(bits, sample_size)

# def public_share(data1, data2):
#     // Publicly shares the data between Alice and Bob
#     // This can be implemented using a public channel
#     share_via_public_channel(data1, data2)

# def abort_protocol():
#     # Aborts the protocol if eavesdropping is detected
#     terminate_protocol()

# def intercept_qubits(qubits):
#     # Eve intercepts the qubits from Alice to Bob
#     return qubits

# def send_qubits_to_bob(qubits):
#     # Sends the (possibly intercepted) qubits to Bob
#     deliver_to_bob(qubits)





