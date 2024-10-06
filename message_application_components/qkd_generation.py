## imports from sequence package

import math

## Method to generate specific number of keys 
def customize_keys(messages):
    max_length = len(max(messages, key=len))
    max_decimal_number = 10**max_length - 1
    bits_needed = math.ceil(math.log2(max_decimal_number + 1))
    return bits_needed
        
class KeyManager:
    def __init__(self, timeline, keysize, num_keys):
        self.timeline = timeline
        self.lower_protocols = []
        self.keysize = keysize
        self.num_keys = num_keys
        self.keys = []
        self.times = []
        
    def send_request(self):
        for p in self.lower_protocols:
            p.push(self.keysize, self.num_keys) # interface for BB84 to generate key
            
    def pop(self, info): # interface for BB84 to return generated keys
        self.keys.append(info)
        self.times.append(self.timeline.now() * 1e-9)


