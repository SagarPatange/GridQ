import matplotlib.pyplot as plt
from .. import message_app

filename = './power_grid_datafiles/power_grid_input.csv'
msg_string = csv_to_string(filename)

distances = [1e3, 5e3, 1e4, 3e4, 7e4, 1e5, 3e5, 7e5, 1e6]
times = []
for i in range (len(distances)):
    times.append(test(sim_time = 1000, msg = msg_string, internode_distance= distances[i], 
            attenuation = 1e-5, polarization_fidelity = 1, eavesdropper_eff = 0.0, backup_qc = True))  # TODO : the input for msg is string list but I only pass in a string so change that 
plt.plot([x / 1e3 for x in distances], [s / 1e9 for s in times], 'o-')
plt.xlabel('Distance (km)')
plt.ylabel('Estimated Real Time (ms)')
plt.title("Distance vs Estimated Real Time")
plt.xscale('log')
plt.show()