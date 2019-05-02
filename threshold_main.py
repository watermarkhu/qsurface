import surface_run
from matplotlib import pyplot as plt
import numpy as np


loadplot = False
new_errors = True
write_errors = False
save_result = True


lattice = "Planar"
lattices = [8]
p = list(np.linspace(0.09, 0.11, 5))
Num = 1000


thresholds = np.zeros((len(lattices),len(p)))
X = np.linspace(p[0], p[-1], 100)
f  = plt.figure()

for lati in range(len(lattices)):
    for pi in range(len(p)):

        print("Calculating for L = ",str(lattices[lati]), "and p =", str(p[pi]))
        no_error_num = 0
        for i in range(Num):

            if i % 1000 == 0: print("Iteration", str(i), ": ")

            if lattice in ["Toric", "toric", "T", "t"]:
                correct = surface_run.toric_2D(laticces[lati], p[pi], 0)
            elif lattice in ["Planar", "planar", "P", "p"]:
                correct = surface_run.planar_2D(lattices[lati], p[pi], 0)
            else:
                exit("Not correct lattice")

            if correct: no_error_num += 1

        thresholds[lati, pi] = no_error_num / Num * 100

    if save_result:
        Name = "./data/" + lattice + "_Thres_L" + str(lattices[lati]) + "_N" + str(Num) + ".txt"
        np.savetxt(Name, thresholds[lati,:])

    fit = np.polyfit(p, thresholds[lati, :], 2)
    polyfit = np.poly1d(fit)
    plt.plot([pi*100 for pi in p], thresholds[lati, :], 'x', color='C'+str(lati))
    plt.plot(X*100, polyfit(X), '-', label=lattices[lati], color='C'+str(lati))


print(thresholds)

plt.title(lattice +" Performance")
plt.xlabel("p (%)")
plt.ylabel("Decoding success rate (%)")
plt.legend()
plt.show()


fname = "./figures/" + lattice + "_thres_N" + str(Num) + ".pdf"
f.savefig(fname, transparent = True, format = "pdf", bbox_inches="tight")
