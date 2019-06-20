import run_multiple
from matplotlib import pyplot as plt
import numpy as np

save_result = True


file_name = "Peeling_toric_only_pX"
plot_name = "Peeling decoder toric lattice with only Pauli error"
lattices = [8, 12, 16, 20]
p = list(np.linspace(0.09, 0.11, 9))
Num = 30000


thresholds = np.zeros((len(lattices), len(p)))
X = np.linspace(p[0], p[-1], 100)
f = plt.figure()

for lati in range(len(lattices)):
    for pi in range(len(p)):

            print("Calculating for L = ", str(lattices[lati]), "and p =", str(p[pi]))

            N_succes = run_multiple.toric_2D_peeling(lattices[lati], 0, p[pi], 0, Num)
            thresholds[lati, pi] = N_succes / Num * 100

    if save_result:
        Name = "./data/" + file_name + "_Thres_L" + str(lattices[lati]) + "_N" + str(Num) + ".txt"
        np.savetxt(Name, thresholds[lati, :])

    fit = np.polyfit(p, thresholds[lati, :], 2)
    polyfit = np.poly1d(fit)
    plt.plot([pi*100 for pi in p], thresholds[lati, :], 'x', color='C'+str(lati))
    plt.plot(X*100, polyfit(X), '-', label=lattices[lati], color='C'+str(lati))


print(thresholds)

plt.title(plot_name + " Performance")
plt.xlabel("p (%)")
plt.ylabel("Decoding success rate (%)")
plt.legend()
plt.show()


if save_result:
    fname = "./figures/" + file_name + "_thres_N" + str(Num) + ".pdf"
    f.savefig(fname, transparent=True, format="pdf", bbox_inches="tight")
