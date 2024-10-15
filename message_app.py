## imports from sequence package
from sequence.kernel.timeline import Timeline
from sequence.message import Message
from sequence.qkd.BB84 import pair_bb84_protocols
from sequence.qkd.cascade import pair_cascade_protocols
from enum import Enum, auto
from sequence.message import Message
from sequence.qkd.cascade import Cascade

## package imports
import numpy as np
import onetimepad

## local repo imports 
from eavesdropper_implemented.node_GridQ import QKDNode_GridQ
from message_application_components.performance_metrics.message_accuracy import compare_strings_with_color
from message_application_components.power_grid_csv_generator import append_json_to_csv
from message_application_components.qkd_generation import KeyManager, customize_keys
from eavesdropper_implemented.BB84_eve import BB84_GridQ

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
        km2 (KeyManager): node 2's key 
        period (float): period (ms) to check the input csv file. The node owner will check for input in csv file at every period of time. 
    '''

    def __init__(self, owner: "QKDNode_GridQ", another: "QKDNode_GridQ", timeline: Timeline, key_manager1: "KeyManager", key_manager2: "KeyManager", qkd_stack_size: "int", internode_distance: "float", attenuation: "float", polarization_fidelity: 'float', eavesdropper_eff: 'float'):  # TODO: change own to owner

        # Nodes
        self.own = owner
        self.another = another

        # Node variables
        self.internode_distance = internode_distance
        self.attenuation = attenuation
        self.polarization_fidelity = polarization_fidelity
        self.eavesdropper_eff = eavesdropper_eff

        # Key Variables
        self.own_keys = np.empty(0)
        self.another_keys = np.empty(0)
        self.km1 = key_manager1
        self.km2 = key_manager2
        self.qkd_stack_size = qkd_stack_size

        # Other Node's MessageManager
        self.another_message_manager = None

        # Components
        self.tl = timeline


        # Message Variables
        self.messages_recieved = []
        self.messages_sent = []
        self.qkd_stack_size = len([element for element in owner.protocol_stack if element])

        # Metrics
        self.time_to_generate_keys = None
        self.total_sim_time = 0

    def pair_message_manager(self, node):
        self.another_message_manager = node    
 
    ## Method to send messages
    def send_message(self, dst: str, messages: list[str]):

        ## Generating right appropriate amount of keys

        key_size = customize_keys(messages)
        num_keys = len(messages)
        self.km1.keysize = key_size
        self.km2.keysize = key_size
        self.km1.num_keys = num_keys
        self.km2.num_keys = num_keys
        
        self.own.set_protocol_layer(0, BB84_GridQ(self.own, self.own.name + ".BB84", self.own.name + ".lightsource", self.own.name + ".qsdetector"))
        self.another.set_protocol_layer(0, BB84_GridQ(self.another, self.another.name + ".BB84", self.another.name + ".lightsource", self.another.name + ".qsdetector"))

        pair_bb84_protocols(self.own.protocol_stack[0], self.another.protocol_stack[0]) 
        if self.qkd_stack_size > 1:
            pair_cascade_protocols(self.own.protocol_stack[1], self.another.protocol_stack[1])
        
        self.km1.lower_protocols[0] = self.own.protocol_stack[self.qkd_stack_size - 1]
        self.own.protocol_stack[self.qkd_stack_size - 1].upper_protocols = [self.km1]
        self.km2.lower_protocols[0] = self.another.protocol_stack[self.qkd_stack_size - 1]
        self.another.protocol_stack[self.qkd_stack_size - 1].upper_protocols = [self.km2]



        self.km1.send_request()
        start_time = self.tl.now()
        self.tl.run()
        end_time = self.tl.now()
        self.time_to_generate_keys = end_time - start_time
        self.own_keys = np.append(self.own_keys,self.km1.keys)
        self.another_keys = np.append(self.another_keys,self.km2.keys)

        encoded_messages = []
        for i in range(len(messages)):
            # encoded_messages.append(otp_encrypt(messages[i], self.own_keys[i])) ## chat-gpt encrypt
            encoded_messages.append(onetimepad.encrypt(messages[i], str(self.own_keys[i]))) ## onetimepad encryption

        ## setting up messaging protocol

        if self.qkd_stack_size > 1:
            self.own.set_protocol_layer(1, None)
            self.another.set_protocol_layer(1, None)

        own_protocol = CrypticMessageExchange(self.own, self.another)
        another_protocol = CrypticMessageExchange(self.another, self.own)
        self.own.set_protocol_layer(0, own_protocol)
        self.another.set_protocol_layer(0, another_protocol)

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
            output_csv_path = './power_grid_datafiles/power_grid_output.csv'
            append_json_to_csv(output_csv_path, decrypted_messages_recieved[i])

        ## Metrics update
        self.total_sim_time = self.tl.now()

        ## delete used keys
        self.own_keys = np.empty(0)
        self.another_keys = np.empty(0)
        self.km1.keys = []
        self.km2.keys = []


        return self.total_sim_time
