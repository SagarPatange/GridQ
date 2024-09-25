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

## package imports
import math
import numpy as np
import json
import onetimepad
import csv

## local repo imports 
from message_application_components.performance_metrics.message_accuracy import compare_strings_with_color
from eavesdropper_implemented.node_GridQ import QKDNode_GridQ
from message_application_components.power_grid_csv_generator import write_input_powergrid_csv_file, csv_to_string, string_to_csv

## Manages QKD keys
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

## Defines the message type
class MessageType(Enum):
    REGULAR_MESSAGE = auto()

## Defines the cryptic message exchange protocol
class CrypticMessageExchange:
    def __init__(self, own: "QKDNode_GridQ", another: "QKDNode_GridQ"):
        self.own = own
        self.another = another
        self.messages_sent = []
        self.messages_recieved = []
        self.name = own.name

    def received_message(self, src: str, msg: "Message"):
        """Method to receive encrypts messages.

        Will perform different processing actions based on the message received.

        Args:
            src (str): source node sending message.
            msg (Message): message received.
        """
        assert src == self.another.name
        if msg.msg_type is MessageType.REGULAR_MESSAGE:
            self.own.protocol_stack[0].messages_recieved.append(msg.text)
            self.another.protocol_stack[0].messages_sent.append(msg.text)

## Defines the attributes sent with the message ## TODO: rename, encrypt message
class EncryptedMessage(Message):
    """Message"""
    def __init__(self, msg_type: MessageType, receiver: str, **kwargs):
        super().__init__(msg_type, receiver)
        self.protocol_type = CrypticMessageExchange
        if self.msg_type == MessageType.REGULAR_MESSAGE:
            self.text = kwargs["the_message"]
        else:
            raise Exception("Generated invalid message type {}".format(msg_type))

## Class containing QKD messaging abilities
class MessageManager:

    '''
    Code for the request application.

    This application has the capabilities to generate keys and send classical
    encrypted messages using the keys generated using QKD. 

    Attributes:
        own (QKDNode_GridQ): the primary node through which messages are sent and recieved
        another (QKDNode_GridQ): the secondary node which massages are recieved and sent
        keys (List[int]): stores the list of keys generated using QKD
        keys (List[int]): stores the list of keys generated using QKD
        another_message_manager (MessageManager): other node's message manager 
        tl (Timeline): timeline object
        cc0 (ClassicalChannel): classical channel end at node 1
        cc1 (ClassicalChannel): classical channel end at node 2
        qc0 (QuantumChannelEve): quantum channel end at node 1
        qc1 (QuantumChannelEve): quantum channel end at node 2
        km1 (KeyManager): node 1's key manager
        km2 (KeyManager): node 2's key manager
    '''

    def __init__(self, own: "QKDNode_GridQ", another: "QKDNode_GridQ", timeline: Timeline):

        # Nodes
        self.own = own
        self.another = another

        # Key Pool
        self.own_keys = np.empty(0)
        self.another_keys = np.empty(0)

        # Other Node's MessageManager
        self.another_message_manager = None

        # Components
        self.tl = timeline
        self.cc0 = None
        self.cc1 = None
        self.qc0 = None
        self.qc1 = None
        self.km1 = None
        self.km2 = None

        # Message Variables
        self.messages_recieved = []
        self.messages_sent = []
        self.qkd_stack_size = len([element for element in own.protocol_stack if element])

        # Metrics
        self.time_to_generate_keys = None
        self.total_sim_time = 0

    
    def pair_message_manager(self, node):
        self.another_message_manager = node

    def generate_keys(self, keysize , num_keys, internode_distance , attenuation, polarization_fidelity, eavesdropper_eff ):
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

        pair_bb84_protocols(self.own.protocol_stack[0], self.another.protocol_stack[0])

        if self.qkd_stack_size > 1:
            pair_cascade_protocols(self.own.protocol_stack[1], self.another.protocol_stack[1])
        cc0 = ClassicalChannel("cc_n1_n2", self.tl, distance=internode_distance, delay = MILLISECOND)
        cc1 = ClassicalChannel("cc_n2_n1", self.tl, distance=internode_distance, delay = MILLISECOND)
        cc0.set_ends(self.own, self.another.name)
        cc1.set_ends(self.another, self.own.name)
        qc0 = QuantumChannelEve("qc_n1_n2", self.tl, attenuation=attenuation, distance=internode_distance,
                            polarization_fidelity=polarization_fidelity, eavesdropper_efficiency = eavesdropper_eff)
        qc1 = QuantumChannelEve("qc_n2_n1", self.tl, attenuation=attenuation, distance=internode_distance,
                            polarization_fidelity=polarization_fidelity, eavesdropper_efficiency = eavesdropper_eff)
        qc0.set_ends(self.own, self.another.name)
        qc1.set_ends(self.another, self.own.name)


        # instantiate our written keysize protocol
        km1 = KeyManager(self.tl, keysize, num_keys)
        km1.lower_protocols.append(self.own.protocol_stack[0])
        self.own.protocol_stack[0].upper_protocols.append(km1)
        km2 = KeyManager(self.tl, keysize, num_keys)
        km2.lower_protocols.append(self.another.protocol_stack[0])
        self.another.protocol_stack[0].upper_protocols.append(km2)
        
        # start simulation and record timing
        self.tl.init()
        km1.send_request()
        self.tl.run()

        ### setting class variabless
        self.time_to_generate_keys = self.tl.now()
        self.own_keys = np.append(self.own_keys,km1.keys)
        self.another_keys = np.append(self.another_keys,km2.keys)
        self.cc0 = cc0
        self.cc1 = cc1
        self.qc0 = qc0
        self.qc1 = qc1
        self.km1 = km1
        self.km2 = km2
    
    ## Method to generate specific number of keys 
    def customize_keys(self, messages, internode_distance, attenuation, polarization_fidelity, eavesdropper_eff):
        max_length = len(max(messages, key=len))
        num_keys = len(messages)
        max_decimal_number = 10**max_length - 1
        bits_needed = math.ceil(math.log2(max_decimal_number + 1))
        self.generate_keys(bits_needed, num_keys, internode_distance, attenuation, polarization_fidelity, eavesdropper_eff)
 
    ## Method to send messages
    def send_message(self, dst: str, messages: list[str], internode_distance, attenuation, polarization_fidelity, eavesdropper_eff):

        ## Generating right appropriate amount of keys
        self.customize_keys(messages, internode_distance, attenuation, polarization_fidelity, eavesdropper_eff)

        encoded_messages = []
        for i in range(len(messages)):
            # encoded_messages.append(otp_encrypt(messages[i], self.own_keys[i])) ## chat-gpt encrypt
            encoded_messages.append(onetimepad.encrypt(messages[i], str(self.own_keys[i]))) ## onetimepad encryption

        self.own.protocol_stack.clear()
        self.own.protocols.clear()
        self.another.protocol_stack.clear()
        self.another.protocols.clear()

        own_protocol = CrypticMessageExchange(self.own, self.another)
        another_protocol = CrypticMessageExchange(self.another, self.own)

        self.own.protocol_stack.append(own_protocol)
        self.own.protocols.append(own_protocol)
        self.another.protocol_stack.append(another_protocol)
        self.another.protocols.append(another_protocol)

        ## send message
        for i in range(len(encoded_messages)):
            msg = EncryptedMessage(MessageType.REGULAR_MESSAGE, self.another.name, the_message = encoded_messages[i])
            if self.another.name == dst:
                self.own.send_message(self.another.name, msg)
            self.tl.run()

        encrypted_messages_recieved = self.another.protocol_stack[0].messages_recieved
        decrypted_messages_recieved = []
        for i in range(len(messages)):
            # decrypted_messages_recieved.append(otp_decrypt(encrypted_messages_recieved[i], self.another_keys[i])) ## chat-gpt encryption
            decrypted_messages_recieved.append(onetimepad.decrypt(encrypted_messages_recieved[i], str(self.another_keys[i]))) ## onetimepad encryption

        ## Update other message manager
        self.messages_sent = messages

        if self.another_message_manager == None:
            print('Add another message manager')
        else:
            self.another_message_manager.messages_recieved = decrypted_messages_recieved

        ## Message Update
        for i in range(len(messages)):
            compare_strings_with_color(messages[i], decrypted_messages_recieved[i])
            string_to_csv(decrypted_messages_recieved[i])

        ## Metrics update
        self.total_sim_time = self.tl.now()
        ## delete used keys
        del self.own_keys
        del self.another_keys

        return self.total_sim_time

## Testing method
def test(sim_time, msg, internode_distance, attenuation, polarization_fidelity, eavesdropper_eff, backup_qc):
    '''
    Test which simulates sending classical messages using QKD, only using the BB84 protocol
    Parameters:
    sim_time: duration of simulation time (ms)
    msg: list of messages needed to be sent
    keysize: size of generated secure key (bits)
    num_keys: number of keys generated (keys)
    internode_distance: distance between two nodes (m)
    attenuation: attenuation (db/km)
    eavesdropper_efficiency = efficacy of eavesdropper
    '''

    ### Initializes Messanger App
    # timeline initialization
    tl = Timeline(sim_time * 1e9)   

    # log_filename = 'log'
    # log.set_logger(__name__, tl, log_filename)
    # log.set_logger_level('DEBUG')
    # modules = ['timeline', 'message_app', 'BB84_eve', 'quantum_channel_eve']
    # for module in modules:
    #     log.track_module(module)

    ######################### Second way of logging
    # level = logging.DEBUG
    # #level = logging.INFO
    # # level = logging.WARNING
    # logging.basicConfig(level=level, filename='', filemode='w')
    


    # node 1 and 2 initialization    
    # Stack size = 1 means only BB84 will be implemented
        
    node1 = QKDNode_GridQ("n1", tl, stack_size=2)    
    node1.set_seed(0)                           
    node2 = QKDNode_GridQ("n2", tl, stack_size=2)     
    node2.set_seed(1)

    # if back up quantum channel exists set a back up quantum channel
    if backup_qc:
        qc0_backup = QuantumChannelEve("qc_n1_n2_backup", tl, attenuation=attenuation, distance=internode_distance,
                                polarization_fidelity=1, eavesdropper_efficiency = 0.0)
        qc1_backup = QuantumChannelEve("qc_n2_n1_backup", tl, attenuation=attenuation, distance=internode_distance,
                                polarization_fidelity=1, eavesdropper_efficiency = 0.0)
        node1.set_backup_qchannel(qc0_backup)
        node2.set_backup_qchannel(qc1_backup) 

    # message manager 1 and 2 initialization and pairing
    n1 = MessageManager(node1, node2, tl)
    n2 = MessageManager(node2, node1, tl)
    n1.pair_message_manager(n2)

    ### Sends message to other node
    # Effects: 1) generates keys for node1 and node2 
    # 2) Encrypts messages using node1's keys and sends to node2
    # 3) Node2 decrypts messages using its keys 
    results = n1.send_message('n2', msg, internode_distance, attenuation, polarization_fidelity, eavesdropper_eff)
    return results

## main function 
if __name__ == "__main__":

    write_input_powergrid_csv_file()
    filename = './power_grid_datafiles/power_grid_input.csv'
    msg_string = csv_to_string(filename)

    time = test(sim_time = 1000, msg = msg_string, internode_distance= 1e3, 
            attenuation = 1e-5, polarization_fidelity = 0.99, eavesdropper_eff = 0.0, backup_qc = True)  # TODO : the input for msg is string list but I only pass in a string so change that 


    print(f'End to end time: {time / 1e9} ms')
    print('Created `power_grid_output.csv`')
        

    

