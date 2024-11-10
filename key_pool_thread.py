from sequence.qkd.BB84 import pair_bb84_protocols
from sequence.qkd.cascade import pair_cascade_protocols
import numpy as np
from eavesdropper_implemented.BB84_eve import BB84_GridQ
from sequence.kernel.timeline import Timeline
from sequence.qkd.BB84 import pair_bb84_protocols
from sequence.qkd.cascade import pair_cascade_protocols
from key_pool_message_app import MessageManager
from message_application_components.qkd_generation import KeyManager
import time

## local repo imports 
from eavesdropper_implemented.node_GridQ import QKDNode_GridQ
from eavesdropper_implemented.BB84_eve import BB84_GridQ

def key_pool_generator(m1: "MessageManager", q):

    while True: 
        if q.get_nowait() == True:
            m1.km1.keysize = 20
            m1.km2.keysize = 20
            m1.km1.num_keys = 5
            m1.km2.num_keys = 5
            m1.own.set_protocol_layer(0, BB84_GridQ(m1.own, m1.own.name + ".BB84", m1.own.name + ".lightsource", m1.own.name + ".qsdetector"))
            m1.another.set_protocol_layer(0, BB84_GridQ(m1.another, m1.another.name + ".BB84", m1.another.name + ".lightsource", m1.another.name + ".qsdetector"))

            pair_bb84_protocols(m1.own.protocol_stack[0], m1.another.protocol_stack[0]) 
            if m1.qkd_stack_size > 1:
                pair_cascade_protocols(m1.protocol_stack[1], m1.another.protocol_stack[1])
            
            m1.km1.lower_protocols[0] = m1.own.protocol_stack[m1.qkd_stack_size - 1]
            m1.own.protocol_stack[m1.qkd_stack_size - 1].upper_protocols = [m1.km1]
            m1.km2.lower_protocols[0] = m1.another.protocol_stack[m1.qkd_stack_size - 1]
            m1.another.protocol_stack[m1.qkd_stack_size - 1].upper_protocols = [m1.km2]

            m1.km1.send_request()
            start_time = m1.tl.now()
            m1.tl.run()
            end_time = m1.tl.now()

            m1.own_keys = np.append(m1.own_keys,m1.km1.keys)
            m1.another_keys = np.append(m1.another_keys,m1.km2.keys)
            time.sleep(5)
            print("tea")
