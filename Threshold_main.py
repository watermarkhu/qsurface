from toric import Toric_lattice
from matplotlib import pyplot as plt
import numpy as np
import time

loadplot = False
base_image_size = 13
plot_indices = False

plot_lattice = False
plot_errors = False
plot_strings = False
new_errors = True
write_errors = False



lattices = [8,12,16,20]
p = np.linspace(0.09, 0.11, 11)
Num = 10000

thresholds = np.zeros((len(lattices),len(p), 3))

for lati in range(len(lattices)):
    for pi in range(len(p)):

        logic0 = []
        logic1 = []
        logic2 = []
        for i in range(Num):

            print("Iteration", str(i), ": ", end="")

            TL = Toric_lattice(lattices[lati], p[pi], loadplot, base_image_size, plot_indices, plot_lattice)
            TL.init_Z_errors(plot_errors, plot_strings, new_errors, write_errors)
            TL.blossom()
            l0, l1, l2 = TL.logical_error()
            logic0.append(l0)
            logic1.append(l1)
            logic2.append(l2)


        thresholds[lati, pi, 0] = sum(logic0) / Num * 100
        thresholds[lati, pi, 1] = sum(logic1) / Num * 100
        thresholds[lati, pi, 2] = sum(logic2) / Num * 100

        print("The threshold for L = ",str(lattices[lati]), "and p =", str(p[pi]), "is", str(thresholds[lati, pi, :]), "% \n")
        print("_______________________________________________________________________\n\n\n")
        time.sleep(1)

np.save("thresholds",thresholds)

f, (ax0, ax1, ax2) = plt.subplots(1,3, sharey = True)

for lati in range(len(lattices)):
    ax0.plot(p * 100, thresholds[lati, :, 0])
    ax1.plot(p * 100, thresholds[lati, :, 1])
    ax2.plot(p * 100, thresholds[lati, :, 2])

ax0.set_title("P0 performance")
ax1.set_title("P0 performance")
ax2.set_title("P0 performance")
ax0.set_xlabel("p (%)")
ax1.set_xlabel("p (%)")
ax2.set_xlabel("p (%)")
ax0.set_ylabel("Decoding success rate (%)")
ax2.legend(lattices)
plt.show()
