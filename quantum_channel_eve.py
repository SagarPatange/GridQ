import heapq as hq

from sequence.kernel.timeline import Timeline
from sequence.topology.node import Node
from sequence.components.photon import Photon
from sequence.components.optical_channel import QuantumChannel
from sequence.kernel.event import Event
from sequence.kernel.process import Process
from sequence.utils import log


class QuantumChannelEve(QuantumChannel):
    """Optical channel for transmission of photons/qubits.

    Attributes:
        name (str): label for channel instance.
        timeline (Timeline): timeline for simulation.
        sender (Node): node at sending end of optical channel.
        receiver (Node): node at receiving end of optical channel.
        attenuation (float): attenuation of the fiber (in dB/m).
        distance (int): length of the fiber (in m).
        polarization_fidelity (float): probability of no polarization error for a transmitted qubit.
        light_speed (float): speed of light within the fiber (in m/ps).
        loss (float): loss rate for transmitted photons (determined by attenuation).
        delay (int): delay (in ps) of photon transmission (determined by light speed, distance).
        frequency (float): maximum frequency of qubit transmission (in Hz).
    """
    def __init__(self, name: str, timeline: "Timeline", attenuation: float, distance: int,
                 polarization_fidelity=1.0, light_speed=2e-4, frequency=8e7, eavesdropper_efficiency = 0.0):
        """Constructor for Quantum Channel class.

        Args:
            name (str): name of the quantum channel instance.
            timeline (Timeline): simulation timeline.
            attenuation (float): loss rate of optical fiber (in dB/m).
            distance (int): length of fiber (in m).
            polarization_fidelity (float): probability of no polarization error for a transmitted qubit (default 1).
            light_speed (float): speed of light within the fiber (in m/ps) (default 2e-4).
            frequency (float): maximum frequency of qubit transmission (in Hz) (default 8e7).
        """

        super().__init__(name, timeline, attenuation, distance, polarization_fidelity, light_speed)
        self.delay = -1
        self.loss = 1
        self.frequency = frequency  # maximum frequency for sending qubits (measured in Hz)
        self.send_bins = []
        self.eavesdropper_efficiency = eavesdropper_efficiency
        self.eavesdropper_present = False
        if eavesdropper_efficiency > 0.0:
            self.eavesdropper_present = True

    def transmit(self, qubit: "Photon", source: "Node") -> None:
            """Method to transmit photon-encoded qubits.

            Args:
                qubit (Photon): photon to be transmitted.
                source (Node): source node sending the qubit.

            Side Effects:
                Receiver node may receive the qubit (via the `receive_qubit` method).
            """

            log.logger.info(
                "{} send qubit with state {} to {} by Channel {}".format(
                    self.sender.name, qubit.quantum_state, self.receiver,
                    self.name))

            assert self.delay >= 0 and self.loss < 1, \
                "QuantumChannel init() function has not been run for {}".format(self.name)
            assert source == self.sender

            # remove lowest time bin
            if len(self.send_bins) > 0:
                time = -1
                while time < self.timeline.now():
                    time_bin = hq.heappop(self.send_bins)
                    time = int(time_bin * (1e12 / self.frequency))
                assert time == self.timeline.now(), "qc {} transmit method called at invalid time".format(self.name)

            # check if photon state using Fock representation
            if qubit.encoding_type["name"] == "fock":
                key = qubit.quantum_state  # if using Fock representation, the `quantum_state` field is the state key.
                # apply loss channel on photonic statex
                self.timeline.quantum_manager.add_loss(key, self.loss)

                # schedule receiving node to receive photon at future time determined by light speed
                future_time = self.timeline.now() + self.delay
                process = Process(self.receiver, "receive_qubit", [source.name, qubit])
                event = Event(future_time, process)
                self.timeline.schedule(event)

            # if not using Fock representation, check if photon kept
            elif (self.sender.get_generator().random() > self.loss) or qubit.is_null:
                if self._receiver_on_other_tl():
                    self.timeline.quantum_manager.move_manage_to_server(
                        qubit.quantum_state)

                if qubit.is_null:
                    qubit.add_loss(self.loss)

                # check if polarization encoding and apply necessary noise
                if (qubit.encoding_type["name"] == "polarization") and (
                        self.sender.get_generator().random() > self.polarization_fidelity):
                    qubit.random_noise(self.get_generator())

                # Implementation of Eve
                # Effects: generates noise if eavesdropper randomlt chooses to intercept qubit
                qubit_polarized = (qubit.encoding_type["name"] == "polarization")
                eavesdropper_effective = (self.sender.get_generator().random() < self.eavesdropper_efficiency)
                if qubit_polarized and self.eavesdropper_present and eavesdropper_effective:
                    qubit.random_noise(self.get_generator())
                
                # schedule receiving node to receive photon at future time determined by light speed
                future_time = self.timeline.now() + self.delay
                process = Process(self.receiver, "receive_qubit", [source.name, qubit])
                event = Event(future_time, process)
                self.timeline.schedule(event)

            # if not using Fock representation, if photon lost, exit
            else:
                pass
