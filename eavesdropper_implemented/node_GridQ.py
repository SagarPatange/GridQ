"""Definitions of node types.

This module provides definitions for various types of quantum network nodes.
All node types inherit from the base Node type, which inherits from Entity.
Node types can be used to collect all the necessary hardware and software for a network usage scenario.
"""

from math import inf
from typing import TYPE_CHECKING, Any, List
import numpy as np

if TYPE_CHECKING:
    from sequence.kernel.timeline import Timeline
    from sequence.message import Message
    from sequence.protocol import StackProtocol
    from sequence.resource_management.memory_manager import MemoryInfo
    from sequence.network_management.reservation import Reservation
    from sequence.components.optical_channel import QuantumChannel, ClassicalChannel
    from sequence.components.memory import Memory
    from sequence.components.photon import Photon
    from sequence.app.random_request import RandomRequestApp

from sequence.kernel.entity import Entity
from sequence.components.memory import MemoryArray
from sequence.components.bsm import SingleAtomBSM
from sequence.components.light_source import LightSource
from sequence.components.detector import QSDetector, QSDetectorPolarization, QSDetectorTimeBin
from sequence.qkd.BB84 import BB84
from sequence.qkd.cascade import Cascade
from sequence.entanglement_management.generation import EntanglementGenerationB
from sequence.resource_management.resource_manager import ResourceManager
from sequence.network_management.network_manager import NewNetworkManager
from sequence.utils.encoding import *
from sequence.utils import log
from eavesdropper_implemented.BB84_eve import BB84_GridQ

from sequence.topology.node import Node, QKDNode

class Node_GridQ(Node):
    """Base node type.
    
    Provides default interfaces for network.

    Attributes:
        name (str): label for node instance.
        timeline (Timeline): timeline for simulation.
        cchannels (Dict[str, ClassicalChannel]): mapping of destination node names to classical channel instances.
        qchannels (Dict[str, QuantumChannel]): mapping of destination node names to quantum channel instances.
        protocols (List[Protocol]): list of attached protocols.
        generator (np.random.Generator): random number generator used by node.
        components (Dict[str, Entity]): mapping of local component names to objects.
        first_component_name (str): name of component that first receives incoming qubits.
    """

    def __init__(self, name: str, timeline: "Timeline", seed=None, component_templates=None):
        """Constructor for node.

        name (str): name of node instance.
        timeline (Timeline): timeline for simulation.
        seed (int): seed for random number generator, default None
        component_templates (Dict[str:Dict]): args for constructing components.
            If not None, should map a component type (specified as a string) to constructor args.
            Default is None.
        """

        log.logger.info("Create Node {}".format(name))
        Entity.__init__(self, name, timeline)
        self.owner = self
        self.cchannels = {}  # mapping of destination node names to classical channels
        self.qchannels = {}  # mapping of destination node names to quantum channels
        self.protocols = []
        self.generator = np.random.default_rng(seed)
        self.components = {}
        self.first_component_name = None
        self.backup_qchannel = None

    def set_backup_qchannel(self,qc):
        self.backup_qchannel = qc


class QKDNode_GridQ(Node_GridQ):
    """Node for quantum key distribution.

    QKDNodes include a protocol stack to create keys.
    The protocol stack follows the "BBN QKD Protocol Suite" introduced in the DARPA quantum network
    (https://arxiv.org/pdf/quant-ph/0412029.pdf page 24).
    The protocol stack is:

    4. Authentication <= No implementation
    3. Privacy Amplification  <= No implementation
    2. Entropy Estimation <= No implementation
    1. Error Correction <= implemented by cascade
    0. Sifting <= implemented by BB84

    Additionally, the `components` dictionary contains the following hardware:

    1. lightsource (LightSource): laser light source to generate keys.
    2. qsdetector (QSDetector): quantum state detector for qubit measurement.

    Attributes:
        name (str): label for node instance.
        timeline (Timeline): timeline for simulation.
        encoding (Dict[str, Any]): encoding type for qkd qubits (from encoding module).
        destination (str): name of destination node for photons
        protocol_stack (List[StackProtocol]): protocols for QKD process.
    """
    def get_protocol_stack (self):
        return self.protocols[0]

    def __init__(self, name: str, timeline: "Timeline", encoding=polarization, stack_size=5,
                 seed=None, component_templates=None):
        """Constructor for the qkd node class.

        Args:
            name (str): label for the node instance.
            timeline (Timeline): simulation timeline.
            encoding (Dict[str, Any]): encoding scheme for qubits (from encoding module) (default polarization).
            stack_size (int): number of qkd protocols to include in the protocol stack (default 5).
        """

        super().__init__(name, timeline, seed)
        if not component_templates:
            component_templates = {}

        self.encoding = encoding
        self.destination = None
        self.counter = 0
        # hardware setup
        ls_name = name + ".lightsource"
        ls_args = component_templates.get("LightSource", {})
        lightsource = LightSource(ls_name, timeline, encoding_type=encoding, **ls_args)
        self.add_component(lightsource)
        lightsource.add_receiver(self)

        qsd_name = name + ".qsdetector"
        if "QSDetector" in component_templates:
            raise NotImplementedError(
                "Configurable parameters for QSDetector in constructor not yet supported.")
        if encoding["name"] == "polarization":
            qsdetector = QSDetectorPolarization(qsd_name, timeline)
        elif encoding["name"] == "time_bin":
            qsdetector = QSDetectorTimeBin(qsd_name, timeline)
        else:
            raise Exception("invalid encoding {} given for QKD node {}".format(encoding["name"], name))
        self.add_component(qsdetector)
        self.set_first_component(qsd_name)

        # add protocols
        self.protocol_stack = [None] * 5

        if stack_size > 0:
            # Create BB84 protocol
            self.protocol_stack[0] = BB84_GridQ(self, name + ".BB84", ls_name, qsd_name)
            self.protocols.append(self.protocol_stack[0])
        if stack_size > 1:
            # Create cascade protocol
            self.protocol_stack[1] = Cascade(self, name + ".cascade")
            self.protocols.append(self.protocol_stack[1])
            self.protocol_stack[0].upper_protocols.append(self.protocol_stack[1])
            self.protocol_stack[1].lower_protocols.append(self.protocol_stack[0])

    def init(self) -> None:
        super().init()
        if self.protocol_stack[0] is not None:
            assert self.protocol_stack[0].role != -1

    def set_protocol_layer(self, layer: int, protocol: "StackProtocol") -> None:
        """Method to set a layer of the protocol stack.

        Args:
            layer (int): layer to change.
            protocol (StackProtocol): protocol to insert.
        """

        if layer < 0 or layer > 4:
            raise ValueError("layer must be between 0 and 4; given {}".format(layer))

        if self.protocol_stack[layer] is not None:
            self.protocols.remove(self.protocol_stack[layer])
        self.protocol_stack[layer] = protocol
        self.protocols.append(protocol)

        if layer > 0 and self.protocol_stack[layer - 1] is not None:
            self.protocol_stack[layer - 1].upper_protocols.append(protocol)
            protocol.lower_protocols.append(self.protocol_stack[layer - 1])

        if layer < 5 and self.protocol_stack[layer + 1] is not None:
            protocol.upper_protocols.append(self.protocol_stack[layer + 1])
            self.protocol_stack[layer + 1].lower_protocols.append(protocol)

    def update_lightsource_params(self, arg_name: str, value: Any) -> None:
        for component in self.components.values():
            if type(component) is LightSource:
                component.__setattr__(arg_name, value)
                return

    def update_detector_params(self, detector_id: int, arg_name: str, value: Any) -> None:
        for component in self.components.values():
            if type(component) is QSDetector:
                component.update_detector_params(detector_id, arg_name, value)
                return

    def get_bits(self, light_time: int, start_time: int, frequency: float, detector_name: str):
        """Method for QKD protocols to get received qubits from the node.

        Uses the detection times from attached detectors to calculate which bits were received.
        Returns 0/1 for successfully transmitted bits and -1 for lost/ambiguous bits.

        Args:
            light_time (int): time duration for which qubits were transmitted.
            start_time (int): time at which qubits were first received.
            frequency (float): frequency of qubit transmission.
            detector_name (str): name of the QSDetector measuring qubits.

        Returns:
            List[int]: list of calculated bits.
        """

        qsdetector = self.components[detector_name]

        # compute received bits based on encoding scheme
        encoding = self.encoding["name"]
        bits = [-1] * int(round(light_time * frequency))  # -1 used for invalid bits

        if encoding == "polarization":
            detection_times = qsdetector.get_photon_times()

            # determine indices from detection times and record bits
            for time in detection_times[0]:  # detection times for |0> detector
                index = round((time - start_time) * frequency * 1e-12)
                if 0 <= index < len(bits):
                    bits[index] = 0

            for time in detection_times[1]:  # detection times for |1> detector
                index = round((time - start_time) * frequency * 1e-12)
                if 0 <= index < len(bits):
                    if bits[index] == 0:
                        bits[index] = -1
                    else:
                        bits[index] = 1
            

        elif encoding == "time_bin":
            detection_times = qsdetector.get_photon_times()
            bin_separation = self.encoding["bin_separation"]
        
            # single detector (for early, late basis) times
            for time in detection_times[0]:
                index = int(round((time - start_time) * frequency * 1e-12))
                if 0 <= index < len(bits):
                    if abs(((index * 1e12 / frequency) + start_time) - time) < bin_separation / 2:
                        bits[index] = 0
                    elif abs(((index * 1e12 / frequency) + start_time) - (time - bin_separation)) < bin_separation / 2:
                        bits[index] = 1
        
            # interferometer detector 0 times
            for time in detection_times[1]:
                time -= bin_separation
                index = int(round((time - start_time) * frequency * 1e-12))
                # check if index is in range and is in correct time bin
                if 0 <= index < len(bits) and \
                        abs(((index * 1e12 / frequency) + start_time) - time) < bin_separation / 2:
                    if bits[index] == -1:
                        bits[index] = 0
                    else:
                        bits[index] = -1

            # interferometer detector 1 times
            for time in detection_times[2]:
                time -= bin_separation
                index = int(round((time - start_time) * frequency * 1e-12))
                # check if index is in range and is in correct time bin
                if 0 <= index < len(bits) and \
                        abs(((index * 1e12 / frequency) + start_time) - time) < bin_separation / 2:
                    if bits[index] == -1:
                        bits[index] = 1
                    else:
                        bits[index] = -1

        else:
            raise Exception("QKD node {} has illegal encoding type {}".format(self.name, encoding))

        return bits

    def set_bases(self, basis_list: List[int], start_time: int, frequency: float, component_name: str):
        """Method to set basis list for measurement component.

        Args:
            basis_list (List[int]): list of bases to measure in.
            start_time (int): time to start measurement.
            frequency (float): frequency with which to measure.
            component_name (str): name of measurement component to edit (normally a QSDetector).
        """

        component = self.components[component_name]
        encoding_type = component.encoding_type
        basis_start_time = start_time - 1e12 / (2 * frequency)

        if encoding_type["name"] == "polarization":
            splitter = component.splitter
            splitter.start_time = basis_start_time
            splitter.frequency = frequency

            splitter_basis_list = []
            for b in basis_list:
                splitter_basis_list.append(encoding_type["bases"][b])
            splitter.basis_list = splitter_basis_list

        elif encoding_type["name"] == "time_bin":
            switch = component.switch
            switch.start_time = basis_start_time
            switch.frequency = frequency
            switch.state_list = basis_list

        else:
            raise Exception("Invalid encoding type for node " + self.name)
    
    def get(self, photon: "Photon", **kwargs):
        self.send_qubit(self.destination, photon)

