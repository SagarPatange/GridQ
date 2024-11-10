## imports from sequence package

from sequence.qkd.BB84 import pair_bb84_protocols
from sequence.qkd.cascade import pair_cascade_protocols
import numpy as np
from eavesdropper_implemented.BB84_eve import BB84_GridQ
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

def generate_10_keys(own, another, qkd_stack_size, km1, km2, tl):
    own.set_protocol_layer(0, BB84_GridQ(own, own.name + ".BB84", own.name + ".lightsource", own.name + ".qsdetector"))
    another.set_protocol_layer(00, BB84_GridQ(another, another.name + ".BB84", another.name + ".lightsource", another.name + ".qsdetector"))

    pair_bb84_protocols(own.protocol_stack[0], another.protocol_stack[0]) 
    if qkd_stack_size > 1:
        pair_cascade_protocols(own.protocol_stack[1], another.protocol_stack[1])
    
    km1.lower_protocols[0] = own.protocol_stack[qkd_stack_size - 1]
    own.protocol_stack[qkd_stack_size - 1].upper_protocols = [km1]
    km2.lower_protocols[0] = another.protocol_stack[qkd_stack_size - 1]
    another.protocol_stack[qkd_stack_size - 1].upper_protocols = [km2]

    km1.send_request()
    start_time = tl.now()
    tl.run()
    end_time = tl.now()

    own_keys = np.append(own_keys,km1.keys)
    another_keys = np.append(another_keys,km2.keys)

    return end_time - start_time


