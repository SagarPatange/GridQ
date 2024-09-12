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
The main program showing the ability of quantum key distribution(QKD) messaging between two different power grid nodes is the `message_app.py` file. A DER contains a utlity control center which is responsible for sending operational instructions to the decentralized nodes in the system. 

The data that DER sends to utility control center contains real numbers (5 numbers from DER to utility control center, and 5 numbers back – P, Q, V, f, angle), integer numbers (2 numbers from DER to utility center – status, mode; and one number back – mode). Each real number is assumed to be a double precision number which takes up 40 bytes each, while each integer number is assumed to be a 32 bit integer which takes up 4 bytes. Together the number could be up to 208 bytes. The `json_generator.py` file is responsible for generating these types of data in the `PowerGridData.json` file so that power grid data transmission can be generated. 

A key which is the size of this data is generated on both (sender and reciever) nodes and then this generated key is used to encrypt, decrypt, send, and recieve messages. More about encryption and decryption is in the `encryption.py` file. There are also eavesdropper simulations implemented into this project to show the benefits and drawbacks of QKD. 

The `eavesdropper_implemented` folder contains modified versions of the original files in SeQUeNCe with the added capabilities of the eavesdropper. These eavesdropper capabilities include:
* Noise generation abilities 
* Back up quantum channel implementation 
* Eavesdropper detection abilities


## Contact
If you have questions, please contact [Sagar Patange] (https://github.com/SagarPatange) at [patange@uchicago.edu].




