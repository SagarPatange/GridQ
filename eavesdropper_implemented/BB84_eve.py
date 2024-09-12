"""Definition of BB84 protocol implementation.

This module provides an implementation of the BB84 protocol for quantum key distribution.
The BB84 class must be attachedd to a node with suitable hardware, such as a QKDNode.
Also included in this module are a function to pair protocol instances (required before the start of transmission) and the message type used by the protocol.
"""

import math
from enum import Enum, auto
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sequence.topology.node import QKDNode

import numpy

from sequence.message import Message
from sequence.protocol import StackProtocol
from sequence.kernel.event import Event
from sequence.kernel.process import Process
from sequence.utils import log
from eavesdropper_implemented.BB84 import BB84, BB84Message, pair_bb84_protocols, BB84MsgType


class BB84Message_GridQ(BB84Message):
    """Message used by BB84 protocols.

    This message contains all information passed between BB84 protocol instances.
    Messages of different types contain different information.

    Attributes:
        msg_type (BB84MsgType): defines the message type.
        receiver (str): name of destination protocol instance.
        frequency (float): frequency for qubit generation (if `msg_type == BEGIN_PHOTON_PULSE`).
        light_time (float): lenght of time to send qubits (if `msg_type == BEGIN_PHOTON_PULSE`).
        start_time (int): simulation start time of qubit pulse (if `msg_type == BEGIN_PHOTON_PULSE`).
        wavelength (float): wavelength (in nm) of photons (if `msg_type == BEGIN_PHOTON_PULSE`).
        bases (List[int]): list of measurement bases (if `msg_type == BASIS_LIST`).
        indices (List[int]): list of indices for matching bases (if `msg_type == MATCHING_INDICES`).
    """

    def __init__(self, msg_type: BB84MsgType, receiver: str, **kwargs):
        Message.__init__(self, msg_type, receiver)
        self.protocol_type = BB84_GridQ
        if self.msg_type is BB84MsgType.BEGIN_PHOTON_PULSE:
            self.frequency = kwargs["frequency"]
            self.light_time = kwargs["light_time"]
            self.start_time = kwargs["start_time"]
            self.wavelength = kwargs["wavelength"]
        elif self.msg_type is BB84MsgType.RECEIVED_QUBITS:
            pass
        elif self.msg_type is BB84MsgType.BASIS_LIST:
            self.bases = kwargs["bases"]
        elif self.msg_type is BB84MsgType.MATCHING_INDICES:
            self.indices = kwargs["indices"]
        else:
            raise Exception("BB84 generated invalid message type {}".format(msg_type))

class BB84_GridQ(BB84):
    """Implementation of BB84 protocol.

    The BB84 protocol uses photons to create a secure key between two QKD Nodes.

    Attributes:
        owner (QKDNode): node that protocol instance is attached to.
        name (str): label for protocol instance.
        role (int): determines if instance is "alice" or "bob" node.
        working (bool): shows if protocol is currently working on a key.
        ready (bool): used by alice to show if protocol currently processing a generate_key request.
        light_time (float): time to use laser (in s).
        start_time (int): simulation start time of key generation.
        photon_delay (int): time delay of photon (ps).
        basis_lists (List[int]): list of bases that qubits are sent in.
        bit_lists (List[int]): list of 0/1 qubits sent (in bases from basis_lists).
        key (int): generated key as an integer.
        key_bits (List[int]): generated key as a list of 0/1 bits.
        another (BB84): other BB84 protocol instance (on opposite node).
        key_lengths (List[int]): list of desired key lengths.
        self.keys_left_list (List[int]): list of desired number of keys.
        self.end_run_times (List[int]): simulation time for end of each request.
    """
    def __init__(self, own: "QKDNode", name: str, lightsource: str, qsdetector: str, role=-1):        
        """Constructor for BB84 class.

        Args:
            own (QKDNode): node hosting protocol instance.
            name (str): name of protocol instance.
            lightsource (str): name of lightsource for QKD
            qsdetector (str): name of QSDetector for QKD

        Keyword Args:
            role (int): 0/1 role defining Alice and Bob protocols (default -1).
        """
        super().__init__(own, name, lightsource, qsdetector, role)

        if own is None:  # used only for unit test purposes
            return
        # super().__init__(own, name)
        self.ls_name = lightsource
        self.qsd_name = qsdetector
        self.role = role

        self.working = False
        self.ready = True  # (for Alice) not currently processing a generate_key request
        self.light_time = 0  # time to use laser (measured in s)
        self.ls_freq = 0  # frequency of light source
        self.start_time = 0  # start time of light pulse
        self.photon_delay = 0  # time delay of photon (including dispersion) (ps)
        self.basis_lists = None
        self.bit_lists = None
        self.key = 0  # key as int
        self.key_bits = None  # key as list of bits
        self.another = None
        self.key_lengths = []  # desired key lengths (from parent)
        self.keys_left_list = []
        self.end_run_times = []
        self.key_generation_time = []
        self.num_of_keys = 0
        self.keys = []
        self.polarization_fideliety = None

        # # metrics
        # self.latency = 0  # measured in seconds
        # self.last_key_time = 0
        # self.throughputs = []  # measured in bits/sec
        # self.error_rates = []

    def push(self, length: int, key_num: int, run_time=1e16) -> None:
        """Method to receive requests for key generation.

        Args:
            length (int): length of key to generate.
            key_num (int): number of keys to generate.
            run_time (int): max simulation time allowed for key generation (default inf).

        Side Effects:
            Will potentially invoke `start_protocol` method to start operations.
        """

        if self.role != 0:
            raise AssertionError("generate key must be called from Alice")

        log.logger.info(self.name + " generating keys, keylen={}, keynum={}".format(length, key_num))
        self.num_of_keys = key_num
        self.key_lengths.append(length)
        self.another.key_lengths.append(length)
        self.keys_left_list.append(key_num)
        end_run_time = run_time + self.owner.timeline.now()
        self.end_run_times.append(end_run_time)
        self.another.end_run_times.append(end_run_time)

        if self.ready:
            self.ready = False
            self.working = True
            self.another.working = True
            self.start_protocol()

    def start_protocol(self) -> None:
        """Method to start protocol.

        When called, this method will begin the process of key generation.
        Parameters for hardware will be calculated, and a `begin_photon_pulse` method scheduled.

        Side Effects:
            Will schedule future `begin_photon_pulse` event.
            Will send a BEGIN_PHOTON_PULSE method to other protocol instance.
        """

        log.logger.debug(self.name + " starting protocol")

        if len(self.key_lengths) > 0:
            # reset buffers for self and another
            self.basis_lists = []
            self.another.basis_lists = []
            self.bit_lists = []
            self.another.bit_lists = []
            self.key_bits = []
            self.another.key_bits = []
            self.latency = 0
            self.another.latency = 0

            self.working = True
            self.another.working = True

            ls = self.owner.components[self.ls_name]
            self.ls_freq = ls.frequency

            # calculate light time based on key length
            self.light_time = self.key_lengths[0] / (self.ls_freq * ls.mean_photon_num)

            # send message that photon pulse is beginning, then send bits
            self.start_time = int(self.owner.timeline.now()) + round(self.owner.cchannels[self.another.owner.name].delay)
            message = BB84Message(BB84MsgType.BEGIN_PHOTON_PULSE, self.another.name,
                                  frequency=self.ls_freq, light_time=self.light_time,
                                  start_time=self.start_time, wavelength=ls.wavelength)
            self.owner.send_message(self.another.owner.name, message)

            process = Process(self, "begin_photon_pulse", [])
            event = Event(self.start_time, process)
            self.owner.timeline.schedule(event)

            self.last_key_time = self.owner.timeline.now()
        else:
            self.ready = True    
        return 

    def begin_photon_pulse(self) -> None:
        """Method to begin sending photons.

        Will calculate qubit parameters and invoke lightsource emit method.
        Also records bits sent for future processing.

        Side Effects:
            Will set destination of photons for local node.
            Will invoke emit method of node lightsource.
            Will schedule another `begin_photon_pulse` event after the emit period.
        """
        
        log.logger.debug(self.name + " starting photon pulse")
        
        if self.working and self.owner.timeline.now() < self.end_run_times[0]:
            self.owner.destination = self.another.owner.name

            # generate basis/bit list
            num_pulses = round(self.light_time * self.ls_freq)    
            basis_list = numpy.random.choice([0, 1], num_pulses)
            bit_list = numpy.random.choice([0, 1], num_pulses)

            # control hardware
            lightsource = self.owner.components[self.ls_name]
            encoding_type = lightsource.encoding_type
            state_list = []
            for i, bit in enumerate(bit_list):
                state = (encoding_type["bases"][basis_list[i]])[bit]
                state_list.append(state)
            lightsource.emit(state_list)

            self.basis_lists.append(basis_list)
            self.bit_lists.append(bit_list)
            self.start_time = self.owner.timeline.now() + int(round(self.light_time * 1e12))
            process = Process(self, "begin_photon_pulse", [])
            event = Event(self.start_time, process)
            self.owner.timeline.schedule(event)

        else:
            self.working = False
            self.another.working = False

            self.key_lengths.pop(0)
            self.keys_left_list.pop(0)
            self.end_run_times.pop(0)
            self.another.key_lengths.pop(0)
            self.another.end_run_times.pop(0)

            # wait for quantum channel to clear of photons, then start protocol
            time = self.owner.timeline.now() + self.owner.qchannels[self.another.owner.name].delay + 1
            process = Process(self, "start_protocol", [])
            event = Event(time, process)
            self.owner.timeline.schedule(event)

    def received_message(self, src: str, msg: "Message") -> None:
        """Method to receive messages.

        Will perform different processing actions based on the message received.

        Args:
            src (str): source node sending message.
            msg (Message): message received.
        """

        if self.working and self.owner.timeline.now() < self.end_run_times[0]:
            if msg.msg_type is BB84MsgType.BEGIN_PHOTON_PULSE:  # (current node is Bob): start to receive photons
                self.ls_freq = msg.frequency
                self.light_time = msg.light_time

                log.logger.debug(self.name + " received BEGIN_PHOTON_PULSE, ls_freq={}, light_time={}, simulation time={}".format(self.ls_freq, self.light_time, self.owner.timeline.now()))

                self.start_time = int(msg.start_time) + self.owner.qchannels[src].delay

                # generate and set basis list
                self.set_measure_basis_list()

                # schedule end_photon_pulse()
                process = Process(self, "end_photon_pulse", [])
                event = Event(self.start_time + round(self.light_time * 1e12) - 1, process)
                self.owner.timeline.schedule(event)
                
            elif msg.msg_type is BB84MsgType.RECEIVED_QUBITS:  # (Current node is Alice): can send basis
                log.logger.debug(self.name + " received RECEIVED_QUBITS message. Simulation time: " + str(self.owner.timeline.now()))
                bases = self.basis_lists.pop(0)
                message = BB84Message(BB84MsgType.BASIS_LIST, self.another.name, bases=bases)
                self.owner.send_message(self.another.owner.name, message)

            elif msg.msg_type is BB84MsgType.BASIS_LIST:  # (Current node is Bob): compare bases
                log.logger.debug(self.name + " received BASIS_LIST message. Simulation time: " + str(self.owner.timeline.now()))
                # parse alice basis list
                basis_list_alice = msg.bases

                # compare own basis with basis message and create list of matching indices
                indices = []
                basis_list = self.basis_lists.pop(0)
                bits = self.bit_lists.pop(0)
                for i, b in enumerate(basis_list_alice):
                    if bits[i] != -1 and basis_list[i] == b:
                        indices.append(i)
                        self.key_bits.append(bits[i])
                # send to Alice list of matching indices
                message = BB84Message(BB84MsgType.MATCHING_INDICES, self.another.name, indices=indices)
                self.owner.send_message(self.another.owner.name, message)

            elif msg.msg_type is BB84MsgType.MATCHING_INDICES:  # (Current node is Alice): create from matching indices
                log.logger.debug(self.name + " received MATCHING_INDICES message. Simulation time: " + str(self.owner.timeline.now()))
                # parse matching indices
                indices = msg.indices

                bits = self.bit_lists.pop(0)

                # set key equal to bits at received indices
                for i in indices:
                    self.key_bits.append(bits[i])

                # check if key long enough. If it is, truncate if necessary and call cascade
                if len(self.key_bits) >= self.key_lengths[0]:
                    throughput = self.key_lengths[0] * 1e12 / (self.owner.timeline.now() - self.last_key_time)

                    while len(self.key_bits) >= self.key_lengths[0] and self.keys_left_list[0] > 0:
                        log.logger.info(self.name + " generated a valid key")
                        self.set_key()  # convert from binary list to int
                        self.another.set_key()
                        self.keys.append(self.key)

                        # for metrics
                        if self.latency == 0:
                            self.latency = (self.owner.timeline.now() - self.last_key_time) * 1e-12

                        self.throughputs.append(throughput)

                        key_diff = self.key ^ self.another.key
                        num_errors = 0
                        while key_diff:
                            key_diff &= key_diff - 1
                            num_errors += 1
                        key_error = num_errors / self.key_lengths[0]
                        self.error_rates.append(num_errors / self.key_lengths[0])
                        polarization_fidelity = self.owner.qchannels[next(iter(self.owner.qchannels))].polarization_fidelity  
                        print(f'Key error: {key_error}')

                        if self.owner.backup_qchannel is not None or self.another.owner.backup_qchannel is not None:                      
                            if key_error > (1 - polarization_fidelity):

                                print(f'Eavesdropper Detected. Discard Key. Error Rate: {key_error}')

                                qc0 = self.owner.qchannels[self.owner.destination]
                                qc1 = self.another.owner.qchannels[self.owner.name]
                                qc0_backup = self.owner.backup_qchannel
                                qc1_backup = self.another.owner.backup_qchannel
                                qc0_backup.set_ends(self.owner, self.owner.destination)
                                qc1_backup.set_ends(self.another.owner, self.owner.name)
                                self.owner.set_backup_qchannel(qc0)
                                self.another.owner.set_backup_qchannel(qc1)
                                self.owner.timeline.events.data.clear()
                                self.another.owner.timeline.events.data.clear()
                                self.start_protocol()

                            else:
                                self.keys_left_list[0] -= 1
                                self.another._pop(info=self.another.key) 
                                self._pop(info=self.key)
                        else:
                            self.keys_left_list[0] -= 1
                            self.another._pop(info=self.another.key) 
                            self._pop(info=self.key)


                        self.key_generation_time.append(self.owner.timeline.now())

                    self.last_key_time = self.owner.timeline.now()
            
                # check if we're done
                if self.keys_left_list[0] < 1:
                    self.working = False
                    self.another.working = False
                        
    def generate_key_times (self):
        return self.key_generation_time
    
    def get_error_rates(self):
        return sum(self.error_rates) / len(self.error_rates)

