from message_app import MessageManager
from eavesdropper_implemented.node_GridQ import QKDNode_GridQ
from qkd_generation import KeyManager
from sequence.kernel.timeline import Timeline
from sequence.components.optical_channel import ClassicalChannel
from eavesdropper_implemented.quantum_channel_eve import QuantumChannelEve
from sequence.qkd.BB84 import pair_bb84_protocols
from sequence.qkd.cascade import pair_cascade_protocols
from enum import Enum, auto
from sequence.message import Message
from sequence.constants import MILLISECOND
import csv, random, os, time, threading, subprocess 
from csv_file_reader_thread import run_shell_command, monitor_csv_file
from message_application_components.power_grid_csv_generator import write_input_to_powergrid_csv_file

def main():

    ################################# Parameter initalization of simulation:
    key_size = 100
    sim_time = 1000               # ms
    polarization_fidelity = 0.97  # 
    attenuation = 1e-5            # db/km 
    internode_distance = 1e3      # km
    eavesdropper_eff = 0.0

    ################################# Initializes components

    # Initialize quantum hardware:
    tl = Timeline(sim_time * 1e9)   # Initializes timeline

    # Initalizing quantum nodes. Stack size = 1 means only BB84 will be implemented, Stack size = 2 means BB84 and Cascade will be implemented
    node1 = QKDNode_GridQ("n1", tl, stack_size=1)    
    node1.set_seed(0)                           
    node2 = QKDNode_GridQ("n2", tl, stack_size=1)     
    node2.set_seed(1)

    # Pairs BB84 and Cascade protocols if applicable. Cascade protocol isn't activated by default due to stack_size = 1
    qkd_stack_size = 1
    pair_bb84_protocols(node1.protocol_stack[0], node2.protocol_stack[0]) 
    if qkd_stack_size > 1:
        pair_cascade_protocols(node1.protocol_stack[1], node2.protocol_stack[1])
        
    # Initalizes classical and quantum channels
    cc0 = ClassicalChannel("cc_n1_n2", tl, distance=internode_distance, delay = MILLISECOND)
    cc1 = ClassicalChannel("cc_n2_n1", tl, distance=internode_distance, delay = MILLISECOND)
    cc0.set_ends(node1, node2.name)
    cc1.set_ends(node2, node1.name)
    qc0 = QuantumChannelEve("qc_n1_n2", tl, attenuation=attenuation, distance=internode_distance,
                        polarization_fidelity=polarization_fidelity, eavesdropper_efficiency = eavesdropper_eff)
    qc1 = QuantumChannelEve("qc_n2_n1", tl, attenuation=attenuation, distance=internode_distance,
                        polarization_fidelity=polarization_fidelity, eavesdropper_efficiency = eavesdropper_eff)
    qc0.set_ends(node1, node2.name)
    qc1.set_ends(node2, node1.name)


    # instantiate our written keysize protocol
    stack_size = 1    
    km1 = KeyManager(tl, keysize, num_keys)
    km1.lower_protocols.append(node1.protocol_stack[stack_size - 1])
    node1.protocol_stack[stack_size - 1].upper_protocols.append(km1)
    km2 = KeyManager(tl, keysize, num_keys)
    km2.lower_protocols.append(node2.protocol_stack[stack_size - 1])
    node2.protocol_stack[stack_size - 1].upper_protocols.append(km2)
    
    # start simulation and record timing
    tl.init()

    # Initalizes back up quantum channel. Set to `False` by default
    backup_qc = False
    if backup_qc:
        qc0_backup = QuantumChannelEve("qc_n1_n2_backup", tl, attenuation=attenuation, distance=internode_distance, polarization_fidelity=1, eavesdropper_efficiency = 0.0)
        qc1_backup = QuantumChannelEve("qc_n2_n1_backup", tl, attenuation=attenuation, distance=internode_distance, polarization_fidelity=1, eavesdropper_efficiency = 0.0)
        node1.set_backup_qchannel(qc0_backup)
        node2.set_backup_qchannel(qc1_backup) 

    # Initalizes message manager 1 and 2 initialization and pairing
    message_manager_1 = MessageManager(node1, node2, tl)
    message_manager_2 = MessageManager(node2, node1, tl)
    message_manager_1.pair_message_manager(message_manager_2)

    ################################# Start of simulation:

    # Create and start a thread for the forever loop
    forever_loop_thread = threading.Thread(target=monitor_csv_file)
    forever_loop_thread.daemon = True  # Daemon thread exits when the main program exits
    forever_loop_thread.start()

    # Run the interactive command input in the main thread
    while True:
        # Allow the user to input terminal commands
        user_command = input("Enter a command to run (type 'exit' to quit and 'generate data' to add data to power_grid_input.csv): ")

        if user_command.lower() == 'exit':
            print("Exiting the program.")
            break

        if user_command.lower() == 'generate data':
            write_input_to_powergrid_csv_file()
            print("Power Grid CSV updated")

        # Start a new thread to execute the user command without blocking the loop
        command_thread = threading.Thread(target=run_shell_command, args=(user_command,))
        command_thread.start()
        
if __name__ == "__main__":
    main()

