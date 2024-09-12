from sequence.kernel.timeline import Timeline
from sequence.topology.node import QKDNode
from sequence.components.optical_channel import ClassicalChannel
from sequence.qkd.BB84 import pair_bb84_protocols
import logging

from eavesdropper_implemented.quantum_channel_eve import QuantumChannelEve

class KeyManager():
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



def test(sim_time, keysize, num_of_keys, test_distance, attenuation_val):
    """
    sim_time: duration of simulation time (ms)
    keysize: size of generated secure key (bits)
    """
    level = logging.DEBUG
    #level = logging.INFO
    # level = logging.WARNING
    logging.basicConfig(level=level, filename='', filemode='w')

    # begin by defining the simulation timeline with the correct simulation time
    tl = Timeline(sim_time * 1e9)
    
    # Here, we create nodes for the network (QKD nodes for key distribution)
    # stack_size=1 indicates that only the BB84 protocol should be included
    n1 = QKDNode("n1", tl, stack_size=2)
    n2 = QKDNode("n2", tl, stack_size=2)
    n1.set_seed(0)
    n2.set_seed(1)
    pair_bb84_protocols(n1.protocol_stack[0], n2.protocol_stack[0])
    
    # connect the nodes and set parameters for the fibers
    # note that channels are one-way
    # construct a classical communication channel
    # (with arguments for the channel name, timeline, and length (in m))
    cc0 = ClassicalChannel("cc_n1_n2", tl, distance=1e3)
    cc1 = ClassicalChannel("cc_n2_n1", tl, distance=1e3)
    cc0.set_ends(n1, n2.name)
    cc1.set_ends(n2, n1.name)
    # construct a quantum communication channel
    # (with arguments for the channel name, timeline, attenuation (in dB/km), and distance (in m))
    # qc0 = QuantumChannelEve("qc_n1_n2", tl, attenuation=attenuation_val, distance=test_distance,
    #                      polarization_fidelity=0.97)
    # qc1 = QuantumChannelEve("qc_n2_n1", tl, attenuation=attenuation_val, distance=test_distance,
    #                      polarization_fidelity=0.97)

    qc0 = QuantumChannelEve("qc_n1_n2", tl, attenuation=attenuation_val, distance=test_distance,
                         polarization_fidelity=0.97, eavesdropper_efficiency = 0.7)
    qc1 = QuantumChannelEve("qc_n2_n1", tl, attenuation=attenuation_val, distance=test_distance,
                         polarization_fidelity=0.97, eavesdropper_efficiency = 0.7)
    qc0.set_ends(n1, n2.name)
    qc1.set_ends(n2, n1.name)

    qc0_backup = QuantumChannelEve("qc_n1_n2_backup", tl, attenuation=attenuation_val, distance=test_distance,
                         polarization_fidelity=0.93, eavesdropper_efficiency = 0.0)
    qc1_backup = QuantumChannelEve("qc_n2_n1_backup", tl, attenuation=attenuation_val, distance=test_distance,
                         polarization_fidelity=0.93, eavesdropper_efficiency = 0.0)
    n1.set_backup_qchannel(qc0_backup)
    n2.set_backup_qchannel(qc1_backup)    

    # instantiate our written keysize protocol
    km1 = KeyManager(tl, keysize, num_of_keys)
    km1.lower_protocols.append(n1.protocol_stack[0])
    n1.protocol_stack[0].upper_protocols.append(km1)
    km2 = KeyManager(tl, keysize, num_of_keys)
    km2.lower_protocols.append(n2.protocol_stack[0])
    n2.protocol_stack[0].upper_protocols.append(km2)
    
    # start simulation and record timing
    tl.init()
    km1.send_request()
    tl.run()
    key_rate_times = n1.get_protocol_stack().generate_key_times()
    error_rates = n1.get_protocol_stack().get_error_rates()
    print(km1.keys, km2.keys)
    return [key_rate_times, error_rates]

print(test(1000, 10, 10, 1e3, 1e-5)[1])