from sequence.kernel.timeline import Timeline
from sequence.topology.node import QKDNode
from sequence.components.optical_channel import ClassicalChannel
from quantum_channel_eve import QuantumChannelEve
from sequence.qkd.BB84 import pair_bb84_protocols
from sequence.message import Message
from enum import Enum, auto
from sequence.message import Message
import math
import numpy as np
import matplotlib.pyplot as plt
import json
from colorama import Fore, Style, init

from node_GridQ import QKDNode_GridQ
# Initialize colorama
init()

def compare_and_print_lists(list1, list2):
    max_len = max(len(list1), len(list2))
    
    # Extend both lists to the maximum length by appending empty strings
    list1.extend([''] * (max_len - len(list1)))
    list2.extend([''] * (max_len - len(list2)))

    # Compare and print the lists with mismatched elements in red
    error_counter = 0
    total_string_length = 0
    letter_differences = 0
    for item1, item2 in zip(list1, list2):
        if item1 != item2:
            print(f"{Fore.RED}{item1}{Style.RESET_ALL}" if item1 else "", end=' ')
            print(f"{Fore.RED}{item2}{Style.RESET_ALL}" if item2 else "")
            error_counter +=1
            total_string_length += len(item1)
            letter_differences += count_character_differences(item1, item2)
        else:
            print(item1, item2)
            total_string_length += len(item1)
    
    return error_counter/len(list1), letter_differences/total_string_length

def count_character_differences(str1, str2):
    max_len = max(len(str1), len(str2))
    str1 = str1.ljust(max_len)
    str2 = str2.ljust(max_len)
    differences = sum(1 for c1, c2 in zip(str1, str2) if c1 != c2)  
    return differences

def load_from_json(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
    return data

#############################################################################################################
##### Manages Keys and forms a pool of keys
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

##### Defines the message type
class MessageType(Enum):
    REGULAR_MESSAGE = auto()

##### Defines the cryptic message exchange protocol
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

##### Defines the attributes sent with the message ## TODO: rename, encrypt message
class EncryptedMessage(Message):
    """Message"""
    def __init__(self, msg_type: MessageType, receiver: str, **kwargs):
        super().__init__(msg_type, receiver)
        self.protocol_type = CrypticMessageExchange
        if self.msg_type == MessageType.REGULAR_MESSAGE:
            self.text = kwargs["the_message"]
        else:
            raise Exception("Generated invalid message type {}".format(msg_type))

##### Plays the role of a messanger_app connecting two clients.
### Contains the generate keys command
### Can make a node send and recieve messages to and from another node            
    
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

        # Metrics
        self.time_to_generate_keys = None
    
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
        cc0 = ClassicalChannel("cc_n1_n2", self.tl, distance=internode_distance)
        cc1 = ClassicalChannel("cc_n2_n1", self.tl, distance=internode_distance)
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

    ## Method to encrypt messages
    def otp_encrypt(self, plaintext, key):
        key_string = str(key)
        if len(plaintext) != len(key_string):
            if len(key_string) > len(plaintext):
                key_string = key_string[len(key_string) - len(plaintext):]  
        encrypted_message = ''.join(chr(ord(p) ^ ord(k)) for p, k in zip(plaintext, key_string))
        return encrypted_message

    ## Method to decrypt messages
    def otp_decrypt(self, ciphertext, key):
        key_string = str(key)
        if len(ciphertext) != len(key_string):
            if len(key_string) > len(ciphertext):
                key_string = key_string[len(key_string) - len(ciphertext):]
        decrypted_message = ''.join(chr(ord(c) ^ ord(k)) for c, k in zip(ciphertext, key_string))
        return decrypted_message
    
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
            encoded_messages.append(self.otp_encrypt(messages[i], self.own_keys[i]))

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
            decrypted_messages_recieved.append(self.otp_decrypt(encrypted_messages_recieved[i], self.another_keys[i]))

        ## Update other message manager
        self.messages_sent = messages

        if self.another_message_manager == None:
            print('Add another message manager')
        else:
            self.another_message_manager.messages_recieved = decrypted_messages_recieved

        ## Message Update
        message_error, character_error = compare_and_print_lists(messages, decrypted_messages_recieved)
        print(f'Percent of messages with error: {message_error}; Percent of characters with error: {character_error}.')
        print(f'Simulation time: {self.time_to_generate_keys}')

        ## delete used keys
        del self.own_keys
        del self.another_keys

        return self.time_to_generate_keys


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

    # node 1 and 2 initialization    
    # Stack size = 1 means only BB84 will be implemented        
    node1 = QKDNode_GridQ("n1", tl, stack_size=1)    
    node1.set_seed(0)                           
    node2 = QKDNode_GridQ("n2", tl, stack_size=1)     
    node2.set_seed(1)

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

######################################################################################################################

if __name__ == "__main__":

    filename = 'random_strings.json'
    strings_list = load_from_json(filename)

    result_list_change = []
    result_list_noChange = []
    for i in range(5):
        results = test(sim_time = 1000, msg = strings_list, internode_distance= 1e3, 
            attenuation = 1e-5, polarization_fidelity = 0.97, eavesdropper_eff = 0.0, backup_qc = True)
        result_list_change.append(results)
    for i in range(5):
        results = test(sim_time = 1000, msg = strings_list, internode_distance= 1e3, 
            attenuation = 1e-5, polarization_fidelity = 0.97, eavesdropper_eff = 0.0, backup_qc = False)
        result_list_noChange.append(results)

    fig = plt.figure(figsize =(10, 7))

    # Creating plot
    plt.boxplot([result_list_noChange, result_list_change])
    plt.xticks([1, 2], ['No-Change', 'Change'])  # Setting labels for the two datasets

    # show plot
    plt.title('Quantum Channel: Change vs No Change')
    plt.show()

        

    

