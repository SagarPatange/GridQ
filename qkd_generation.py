def generate_keys(sender, reciever, qkd_stack_size, t1, keysize , num_keys, internode_distance , attenuation, polarization_fidelity, eavesdropper_eff ):
    """
    Method to generate a specific amount of keys based on the size of the messages

    Parameters:
    sim_time: duration of simulation time (ms)
    keysize: size of generated secure key (bits)
    num_keys: number of keys generated (keys)
    internode_distance: distance between two nodes (m)
    attenuation: attenuation (db/km)
    eavesdropper_efficiency = efficacy of eavesdropper
    """
    # begin by defining the simulation timeline with the correct simulation time

    pair_bb84_protocols(sender.protocol_stack[0], receiver.protocol_stack[0])

    if qkd_stack_size > 1:
        pair_cascade_protocols(sender.protocol_stack[1], receiver.protocol_stack[1])
        
    cc0 = ClassicalChannel("cc_n1_n2", tl, distance=internode_distance, delay = MILLISECOND)
    cc1 = ClassicalChannel("cc_n2_n1", tl, distance=internode_distance, delay = MILLISECOND)
    cc0.set_ends(sender, receiver.name)
    cc1.set_ends(receiver, sender.name)
    qc0 = QuantumChannelEve("qc_n1_n2", tl, attenuation=attenuation, distance=internode_distance,
                        polarization_fidelity=polarization_fidelity, eavesdropper_efficiency = eavesdropper_eff)
    qc1 = QuantumChannelEve("qc_n2_n1", tl, attenuation=attenuation, distance=internode_distance,
                        polarization_fidelity=polarization_fidelity, eavesdropper_efficiency = eavesdropper_eff)
    qc0.set_ends(sender, receiver.name)
    qc1.set_ends(receiver, sender.name)


    # instantiate our written keysize protocol
    stack_index = qkd_stack_size - 1
    km1 = KeyManager(tl, keysize, num_keys)
    km1.lower_protocols.append(sender.protocol_stack[stack_index])
    sender.protocol_stack[stack_index].upper_protocols.append(km1)
    km2 = KeyManager(tl, keysize, num_keys)
    km2.lower_protocols.append(receiver.protocol_stack[stack_index])
    receiver.protocol_stack[stack_index].upper_protocols.append(km2)
    
    # start simulation and record timing
    tl.init()
    km1.send_request()
    tl.run()

    ### setting class variabless
    self.time_to_generate_keys = tl.now()
    sender_keys = np.append(sender_keys,km1.keys)
    receiver_keys = np.append(receiver_keys,km2.keys)
    self.cc0 = cc0
    self.cc1 = cc1
    self.qc0 = qc0
    self.qc1 = qc1
    self.km1 = km1
    self.km2 = km2

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


