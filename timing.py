import run_multiple
from matplotlib import pyplot as plt
import numpy as np
import time
import random

lattices = [8, 12, 16]
p =  list(np.linspace(0.09, 0.11, 9))
Num = 10000

colors = ['r','g','b']
timing = np.zeros((3, len(lattices),len(p)))
f  = plt.figure()


for lati in range(len(lattices)):
    for pi in range(len(p)):

        print("Calculating for L = ",str(lattices[lati]), "and p =", str(p[pi]))
        tMe = 0
        tNi = 0
        tEd = 0

        t0 = time.time()
        print("Own")
        correct = run_multiple.toric_2D_MWPM(lattices[lati], p[pi], 0, Num)
        t1 = time.time()
        print("Nickerson")
        correct = run_multiple.toric_2D_nickerson(lattices[lati], p[pi], 0, Num)
        t2 = time.time()
        print("Eduardo")
        correct = run_multiple.toric_2D_eduardo(lattices[lati], p[pi], 0, Num)
        t3 = time.time()

        tMe = t1 - t0
        tNi = t2 - t1
        tEd = t3 - t2

        timing[0,lati,pi] = tMe/Num*1000
        timing[1,lati,pi] = tNi/Num*1000
        timing[2,lati,pi] = tEd/Num*1000

    plt.plot(timing[0,lati,:], '-',  lw = 2, c = colors[lati], label = "Own L=" + str(lattices[lati]))
    plt.plot(timing[1,lati,:], '--', lw = 2, c = colors[lati], label = "Nickerson L=" + str(lattices[lati]))
    plt.plot(timing[2,lati,:], ':', lw = 2, c = colors[lati], label = "Eduardo L=" + str(lattices[lati]))


print(timing)

plt.title("Average runtime")
plt.xlabel("p (%)")
plt.ylabel("Average time (ms)")
plt.legend()
plt.show()

fname = "./figures/timing_comparison_toric_thres_N" + str(Num) + ".pdf"
f.savefig(fname, transparent = True, format = "pdf", bbox_inches="tight")
