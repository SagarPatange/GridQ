## imports from sequence package
from sequence.kernel.timeline import Timeline
from sequence.components.optical_channel import ClassicalChannel
from eavesdropper_implemented.quantum_channel_eve import QuantumChannelEve
from sequence.qkd.BB84 import pair_bb84_protocols
from sequence.qkd.cascade import pair_cascade_protocols
from sequence.message import Message
from enum import Enum, auto
from sequence.message import Message
import sequence.utils.log as log
from sequence.constants import MILLISECOND
import logging
import math

## Method to generate specific number of keys 
def customize_keys(messages):
    max_length = len(max(messages, key=len))
    num_keys = len(messages)
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


