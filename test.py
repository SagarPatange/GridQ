# Import libraries
import matplotlib.pyplot as plt
import numpy as np


# Creating dataset
np.random.seed(10)
data = np.random.normal(100, 20, 200)
data1 = np.random.normal(100, 10, 200)

data_2 = [data, data1]
fig = plt.figure(figsize =(10, 7))

# Creating plot
plt.boxplot(data_2)

# show plot
plt.xticks([1, 2], ['No-Change', 'Change'])  # Setting labels for the two datasets
plt.title('Quantum Channel: Change vs No Change')
plt.show()