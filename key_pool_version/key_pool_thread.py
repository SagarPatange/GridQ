from sequence.qkd.BB84 import pair_bb84_protocols
from sequence.qkd.cascade import pair_cascade_protocols
import numpy as np
from eavesdropper_implemented.BB84_eve import BB84_GridQ
from sequence.kernel.timeline import Timeline
from sequence.qkd.BB84 import pair_bb84_protocols
from sequence.qkd.cascade import pair_cascade_protocols
import time
from message_application_components.qkd_generation import KeyManager

## local repo imports 
from eavesdropper_implemented.node_GridQ import QKDNode_GridQ
from eavesdropper_implemented.BB84_eve import BB84_GridQ

def key_pool_generator(owner: "QKDNode_GridQ", another: "QKDNode_GridQ", tl: Timeline, key_manager1: "KeyManager", key_manager2: "KeyManager", qkd_stack_size: "int", q):

    while True: 
        while True and q == 1:
            owner.set_protocol_layer(10, BB84_GridQ(owner, owner.name + ".BB84", owner.name + ".lightsource", owner.name + ".qsdetector"))
            another.set_protocol_layer(10, BB84_GridQ(another, another.name + ".BB84", another.name + ".lightsource", another.name + ".qsdetector"))

            pair_bb84_protocols(owner.protocol_stack[0], another.protocol_stack[0]) 
            if qkd_stack_size > 1:
                pair_cascade_protocols(owner.protocol_stack[1], another.protocol_stack[1])
            
            key_manager1.lower_protocols[0] = owner.protocol_stack[qkd_stack_size - 1]
            owner.protocol_stack[qkd_stack_size - 1].upper_protocols = [key_manager1]
            key_manager2.lower_protocols[0] = another.protocol_stack[qkd_stack_size - 1]
            another.protocol_stack[qkd_stack_size - 1].upper_protocols = [key_manager2]

            key_manager1.send_request()
            start_time = tl.now()
            tl.run()
            end_time = tl.now()

            own_keys = np.append(own_keys,key_manager1.keys)
            another_keys = np.append(another_keys,key_manager2.keys)

            return end_time - start_time