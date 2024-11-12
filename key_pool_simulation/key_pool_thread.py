from sequence.qkd.BB84 import pair_bb84_protocols
from sequence.qkd.cascade import pair_cascade_protocols
import numpy as np
from eavesdropper_implemented.BB84_eve import BB84_GridQ
from sequence.qkd.BB84 import pair_bb84_protocols
from sequence.qkd.cascade import pair_cascade_protocols
from key_pool_simulation.key_pool_message_app import MessageManager
import time

## local repo imports 
from eavesdropper_implemented.BB84_eve import BB84_GridQ

def key_pool_generator(max_key_pool_size, m1: "MessageManager", qkd_run):

    while not qkd_run.is_set(): 
        if len(m1.own_keys) < max_key_pool_size:
            m1.km1.keysize = 20
            m1.km2.keysize = 20
            m1.km1.num_keys = 10
            m1.km2.num_keys = 10
            m1.own.set_protocol_layer(0, BB84_GridQ(m1.own, m1.own.name + ".BB84", m1.own.name + ".lightsource", m1.own.name + ".qsdetector"))
            m1.another.set_protocol_layer(0, BB84_GridQ(m1.another, m1.another.name + ".BB84", m1.another.name + ".lightsource", m1.another.name + ".qsdetector"))

            pair_bb84_protocols(m1.own.protocol_stack[0], m1.another.protocol_stack[0]) 
            if m1.qkd_stack_size > 1:
                pair_cascade_protocols(m1.own.protocol_stack[1], m1.another.protocol_stack[1])
            
            m1.km1.lower_protocols[0] = m1.own.protocol_stack[m1.qkd_stack_size - 1]
            m1.own.protocol_stack[m1.qkd_stack_size - 1].upper_protocols = [m1.km1]
            m1.km2.lower_protocols[0] = m1.another.protocol_stack[m1.qkd_stack_size - 1]
            m1.another.protocol_stack[m1.qkd_stack_size - 1].upper_protocols = [m1.km2]

            m1.km1.send_request()
            m1.tl.run()

            m1.own_keys = np.append(m1.own_keys,m1.km1.keys)
            m1.another_keys = np.append(m1.another_keys,m1.km2.keys)
        else:
            time.sleep(1)
            

