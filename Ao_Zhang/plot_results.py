import matplotlib
matplotlib.use("tkagg")
import matplotlib.pyplot as plt
import numpy as np

current_test = "test_d"
N = 100
d = "all"
sigma = 0.1

E_in = np.load("saved_results/" + current_test + "N_"+ str(N) +"_d_" + str(d) + "_sig_" + str(sigma) + "_Ein.npy")
E_out = np.load("saved_results/" + current_test + "N_"+ str(N) +"_d_" + str(d) + "_sig_" + str(sigma) + "_Eout.npy")
E_bias = np.load("saved_results/" + current_test + "N_"+ str(N) +"_d_" + str(d) + "_sig_" + str(sigma) + "_Ebias.npy")

x = np.arange(21)


fig = plt.figure(figsize = (8, 8))
ax1 = fig.add_subplot(111)
ax1.plot(x, E_in, "r")
ax1.plot(x, E_out, "g")
ax1.plot(x, E_bias, "b")
plt.show()