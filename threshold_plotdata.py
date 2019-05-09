from matplotlib import pyplot as plt
import numpy as np

lattice = "Planar"
lattices = [8,12,16,20]
p = list(np.linspace(0.09, 0.11,9))
Num = 20000



X = np.linspace(p[0], p[-1], 100)
f  = plt.figure()


for lati in range(len(lattices)):
    Name = "./data/" + lattice + "_Thres_L" + str(lattices[lati]) + "_N" + str(Num) + ".txt"
    thresholds = np.loadtxt(Name)
    fit = np.polyfit(p, thresholds, 2)
    polyfit = np.poly1d(fit)
    plt.plot([pi*100 for pi in p], thresholds, 'x', color='C'+str(lati))
    plt.plot(X*100, polyfit(X), '-', label=lattices[lati], color='C'+str(lati))

plt.title("performance planar")
plt.legend()
plt.xlabel("p (%)")
plt.ylabel("Decoding success rate (%)")
plt.show()
fname = "./figures/" + lattice + "_thres_N" + str(Num) + ".pdf"
f.savefig(fname, transparent = True, format = "pdf", bbox_inches="tight")
