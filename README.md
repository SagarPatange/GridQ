<p align="center">
  <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/sequence-toolbox/SeQUeNCe/master/docs/Sequence_Icon_Name_Dark.png">
   <img src="https://raw.githubusercontent.com/sequence-toolbox/SeQUeNCe/master/docs/Sequence_Icon_Name.svg" alt="sequence icon" width="450" class="center">
  </picture>
</p>

<h3><p align="center">Communitcation using Quantum Key Distribution</p></h3>

<br>

## Grid-Q: Quantum Key Distribution Messaging Project

Grid-Q is a project which implements Argonne's quantum network simualtor(SeQUeNCe) on a distrubuted energy resouce(DER) by creating an app which focuses on generating keys using quantum key distribution (QKD) and then exchanging messages between two different nodes. 

To see how Argonne's SeQUeNCe simulator works please visit the website https://github.com/sequence-toolbox/SeQUeNCe. SeQUeNCe is an open source, discrete-event simulator for quantum networks. As described in their [paper](http://arxiv.org/abs/2009.12000), the simulator includes 5 modules on top of a simulation kernel:
* Hardware
* Entanglement Management
* Resource Management
* Network Management
* Application

These modules can be edited by users to define additional functionality and test protocol schemes, or may be used as-is to test network parameters and topologies.

Please visit their GitHub page for more information

## Citation
Please cite us, thank you!
```
Coming soon!
```

## Usage 
There are three main programs in this project. 
1) `Dockerfile`
2) `main.py`
3) `power_grid_simulated_main.py`

The Dockerfile is used to run `main.py`. When it is run, the `main.py` file will constantly read the target csv data file `power_grid_input.csv` which is in the `power_grid_datafiles`. Oak Ridge National Lab's program in its own docker container is supposed to interact with the `power_grid_input.csv` data file to add new power grid data but this implementation is still in progress. 

To run the Dockerfile, please use the commands `docker build -t power_grid .` and `docker run power_grid` to build the image and run the image respectively. 

Hence, the `power_grid_simulated_main.py` file was created to simulate the data coming into the `power_grid_input.csv`. Once the program is run, the `power_grid_simulated_main.py` file will allow the user to type in `generate data` into the command prompt to generate data into the `power_grid_input.csv` data file. Once this newly generated data is detected by `power_grid_simulated_main.py`, a messaging application will generate keys using quantum key distribution between two nodes (sender and reciever node). After the sender sends the encrypted message to the reciever, the messages will then be decrypted using the shared symetric quantum key. The message relayed onto the sender node will show up on the `power_grid_output.csv` include extra metrics of data regarding the simulation time  

Both of the main files contain changeable parameters at the beginning of the script allowing for easy testing of different quantum systems. Parameters include:

1) sim_time (float): estimated real time allowed for key generation simulation to run
2) polarization_fidelity (float): fidelity of quantum channel, probability of qubit being unaffected by noise.
3) attenuation (float): standard value for attenuation (db/m)
4) internode_distance (float): distance between two nodes (km)
5) qubit_frequency (float): maximum frequency of qubit transmission (in Hz) (default 8e7).
6) eavesdropper_eff (float): added noise which is the probability of qubit being affected by noise of an eavesdropper.
7) stack_size (int: 1, 2, 3, 4, or 5): 1) only BB84 implemented in QKD, 2) BB84 and Cascade implemented in QKD
8) frequency (float): frequency (in Hz) of photon creation (default 8e7).
9) wavelength (float): wavelength (in nm) of emitted photons (default 1550).
10) bandwidth (float): st. dev. in photon wavelength (default 0).
11) mean_photon_num (float): mean number of photons emitted each period (default 0.1).
12) phase error 

The data that is being sent from one node to another contains 5 real numbers (5 numbers from DER to utility control center, and 5 numbers back – P, Q, V, f, angle), 2 integer numbers (2 numbers from DER to utility center – status, mode; and one number back – mode). Each real number is assumed to be a double precision number which takes up 40 bytes each, while each integer number is assumed to be a 32 bit integer which takes up 4 bytes. Together the number could be up to 208 bytes. The `power_grid_csv_generator.py` file is responsible for generating these types of data in the input and output csv files. 

A key which is the size of this data is generated on both (sender and reciever) nodes and then this generated key is used to encrypt, decrypt, send, and recieve messages. More about encryption and decryption is in the `encryption.py` file. There are also eavesdropper simulations implemented into this project to show the benefits and drawbacks of QKD. 

The `eavesdropper_implemented` folder contains modified versions of the original files in SeQUeNCe with the added capabilities of the eavesdropper. These eavesdropper capabilities include:
* Noise generation abilities 
* Back up quantum channel implementation 
* Eavesdropper detection abilities


## Contact
If you have questions, please contact [Sagar Patange] (https://github.com/SagarPatange) at [patange@uchicago.edu].




