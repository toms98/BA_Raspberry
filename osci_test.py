import matplotlib.pyplot as plt

data = [4, 7, 1, 9, 5, 2, 8]
#Remove Toolbar from MatPlotLib
plt.rcParams['toolbar'] = 'None'
plt.plot(data)
plt.show()