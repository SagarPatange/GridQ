from key_pool_simulation.key_pool_message_app import MessageManager
from eavesdropper_implemented.node_GridQ import QKDNode_GridQ
from message_application_components.qkd_generation import KeyManager
from sequence.kernel.timeline import Timeline
from sequence.components.optical_channel import ClassicalChannel
from eavesdropper_implemented.quantum_channel_eve import QuantumChannelEve
from sequence.qkd.BB84 import pair_bb84_protocols
from sequence.qkd.cascade import pair_cascade_protocols
from sequence.constants import MILLISECOND
import threading, queue, json
from message_application_components.csv_file_reader_thread import monitor_csv_file, user_input
from message_application_components.power_grid_csv_generator import erase_powergrid_csv_data, read_csv_nth_row
from key_pool_simulation.key_pool_thread import key_pool_generator

def main():
    '''
    
    '''
    ################################# Parameter initalization of simulation:

    # General Simulation Variables
    sim_time = 1e6                # sim_time (float): estimated real time allowed for key generation simulation to run
    polarization_fidelity = 1     # polarization_fidelity (float): fidelity of quantum channel, probability of qubit being unaffected by noise. 
    attenuation = 2e-4            # standard value for attenuation (db/m) 
    internode_distance = 1e3      # internode_distance (float): distance between two nodes (km)
    qubit_frequency = 8e7         # qubit_frequency (float): maximum frequency of qubit transmission (in Hz) (default 8e7).
    eavesdropper_eff = 0.0        # eavesdropper_eff (float): added noise which is the probability of qubit being affected by noise of an eavesdropper. 
    qkd_stack_size = 1            # stack_size (int: 1, 2, 3, 4, or 5): 1) only BB84 implemented in QKD, 2) BB84 and Cascade implemented in QKD
    backup_qc = False

    # Lightsource Variables 
    frequency=1e6                 # frequency (float): frequency (in Hz) of photon creation (default 8e7).
    wavelength=1550               # wavelength (float): wavelength (in nm) of emitted photons (default 1550).
    bandwidth=0                   # bandwidth (float): st. dev. in photon wavelength (default 0).
    mean_photon_num=0.1           # mean_photon_num (float): mean number of photons emitted each period (default 0.1).
    phase_error=0                 # phase_error (float): phase error applied to qubits (default 0).
    # 
    
    component_templates = {"LightSource": {"frequency": frequency, "wavelength": wavelength, "bandwidth": bandwidth, "mean_photon_num": mean_photon_num, "phase_error": phase_error}}
    ## TODO: create a dictionary of arguments to pass into the lightsource 


    ################################# Initializes components

    # Initialize quantum hardware:
    tl = Timeline(sim_time * 1e9)   # Initializes timeline

    # Initalizing quantum nodes. Stack size = 1 means only BB84 will be implemented, Stack size = 2 means BB84 and Cascade will be implemented
    node1 = QKDNode_GridQ("n1", tl, stack_size=qkd_stack_size, component_templates=component_templates)    
    node1.set_seed(0)                           
    node2 = QKDNode_GridQ("n2", tl, stack_size=qkd_stack_size, component_templates=component_templates)     
    node2.set_seed(1)

    # Pairs BB84 and Cascade protocols if applicable. Cascade protocol isn't activated by default due to stack_size = 1
    pair_bb84_protocols(node1.protocol_stack[0], node2.protocol_stack[0]) 
    if qkd_stack_size > 1:
        pair_cascade_protocols(node1.protocol_stack[1], node2.protocol_stack[1])
        
    # Initalizes classical and quantum channels
    cc0 = ClassicalChannel("cc_n1_n2", tl, distance=internode_distance, delay = MILLISECOND)
    cc1 = ClassicalChannel("cc_n2_n1", tl, distance=internode_distance, delay = MILLISECOND)
    cc0.set_ends(node1, node2.name)
    cc1.set_ends(node2, node1.name)
    qc0 = QuantumChannelEve("qc_n1_n2", tl, attenuation=attenuation, distance=internode_distance,
                        polarization_fidelity=polarization_fidelity, frequency= qubit_frequency, eavesdropper_efficiency = eavesdropper_eff)
    qc1 = QuantumChannelEve("qc_n2_n1", tl, attenuation=attenuation, distance=internode_distance,
                        polarization_fidelity=polarization_fidelity, frequency= qubit_frequency, eavesdropper_efficiency = eavesdropper_eff)
    qc0.set_ends(node1, node2.name)
    qc1.set_ends(node2, node1.name)

    # instantiate our written keysize protocol
    km1 = KeyManager(tl, keysize = 0, num_keys = 0)
    km1.lower_protocols.append(node1.protocol_stack[qkd_stack_size - 1])
    node1.protocol_stack[qkd_stack_size - 1].upper_protocols.append(km1)
    km2 = KeyManager(tl, keysize = 0, num_keys = 0)
    km2.lower_protocols.append(node2.protocol_stack[qkd_stack_size - 1])
    node2.protocol_stack[qkd_stack_size - 1].upper_protocols.append(km2)
    
    # start simulation and record timing
    tl.init()

    # Initalizes back up quantum channel. Set to `False` by default
    if backup_qc:
        qc0_backup = QuantumChannelEve("qc_n1_n2_backup", tl, attenuation=attenuation, distance=internode_distance, polarization_fidelity=1, frequency= qubit_frequency, eavesdropper_efficiency = 0.0)
        qc1_backup = QuantumChannelEve("qc_n2_n1_backup", tl, attenuation=attenuation, distance=internode_distance, polarization_fidelity=1, frequency= qubit_frequency, eavesdropper_efficiency = 0.0)
        node1.set_backup_qchannel(qc0_backup)
        node2.set_backup_qchannel(qc1_backup) 

    # Initalizes message manager 1 and 2 initialization and pairing
    message_manager_1 = MessageManager(node1, node2, tl, km1, km2, qkd_stack_size, internode_distance, attenuation, polarization_fidelity, eavesdropper_eff)
    message_manager_2 = MessageManager(node2, node1, tl, km2, km1, qkd_stack_size, internode_distance, attenuation, polarization_fidelity, eavesdropper_eff)
    message_manager_1.pair_message_manager(message_manager_2)

    ################################# Start of simulation:

    # Clears the `power_grid_input.csv` file 
    erase_powergrid_csv_data('./power_grid_datafiles/power_grid_input.csv')
    erase_powergrid_csv_data('./power_grid_datafiles/power_grid_output.csv')

    q1 = queue.Queue()
    qkd_run = threading.Event()

    # Create and start a thread for the forever loop
    forever_loop_thread = threading.Thread(target=monitor_csv_file, args=('./power_grid_datafiles/power_grid_input.csv', 1, q1))
    forever_loop_thread.daemon = True  # Daemon thread exits when the main program exits
    forever_loop_thread.start()

    ##################################################### TODO: write a different program to get the input 
    # Continually check for user input in the shell
    user_input_thread = threading.Thread(target=user_input)
    user_input_thread.daemon = True  # Daemon thread
    user_input_thread.start()

    ##################################################### 
    # Continually check for user input in the shell
    qkd_thread = threading.Thread(target=key_pool_generator, args=(message_manager_1, qkd_run))
    qkd_thread.daemon = True  # Daemon thread exits when the main program exits
    qkd_thread.start()

    #####################################################
    # Run the interactive command input in the main 
    current_csv_row = 1
    new_csv_row = 1

    print("Enter a command (type 'exit' to quit and 'generate data' to add data to power_grid_input.csv): ")

    while True:
        # Check if there are new results in the queue
        try:
            while not q1.empty():
                new_csv_row = q1.get_nowait()  # Non-blocking get
                print(f"\nNew data added to row {new_csv_row - 1} of power_grid_output.csv")
        except queue.Empty:
            pass
        
        if new_csv_row > current_csv_row:
            qkd_run.set()
            qkd_thread.join()

            for i in range(current_csv_row , new_csv_row ):
                row_data = read_csv_nth_row('./power_grid_datafiles/power_grid_input.csv', i)
                parsed_data = list(json.loads(row_data).values())
                message_manager_1.send_message(node2.name, parsed_data)
            current_csv_row = new_csv_row

            qkd_thread = threading.Thread(target=key_pool_generator, args=(message_manager_1, qkd_run))
            qkd_thread.daemon = True  # Daemon thread exits when the main program exits
            qkd_thread.start()
            

if __name__ == "__main__":
    main()

