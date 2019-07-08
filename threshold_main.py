import run_multiple
from matplotlib import pyplot as plt
import numpy as np
import time

save_result = True

file_name = "Peeling_toric_only_pX_bucket_ncount"
plot_name = "Peeling decoder toric lattice with only Pauli error - bucket, ncount"
lattices = [8, 12, 16, 20]
p = list(np.linspace(0.09, 0.11, 11))
Num = 30000


thresholds = np.zeros((len(lattices), len(p)))
computimes = np.zeros((len(lattices), len(p)))
X = np.linspace(p[0], p[-1], 100)
f0 = plt.figure()
f1 = plt.figure()

for lati in range(len(lattices)):
    for pi in range(len(p)):

            print("Calculating for L = ", str(lattices[lati]), "and p =", str(p[pi]))

            t0 = time.time()

            N_succes = run_multiple.toric_2D_peeling(lattices[lati], 0, p[pi], 0, Num, plot_load=False)

            t1 = time.time()

            thresholds[lati, pi] = N_succes / Num * 100
            computimes[lati, pi] = t1 - t0

    if save_result:
        Name = "./data/" + file_name + "_Thres_L" + str(lattices[lati]) + "_N" + str(Num) + ".txt"
        np.savetxt(Name, thresholds[lati, :])

    plt.figure(f0.number)
    fit = np.polyfit(p, thresholds[lati, :], 2)
    polyfit = np.poly1d(fit)
    plt.plot([pi*100 for pi in p], thresholds[lati, :], '.', color='C'+str(lati), ms=10)
    plt.plot(X*100, polyfit(X), '-', label=lattices[lati], color='C'+str(lati), lw=2, alpha=0.8)

    plt.figure(f1.number)
    fit = np.polyfit(p, computimes[lati, :], 2)
    polyfit = np.poly1d(fit)
    plt.plot([pi*100 for pi in p], computimes[lati, :], '.', color='C'+str(lati), ms=10)
    plt.plot(X*100, polyfit(X), '-', label=lattices[lati], color='C'+str(lati), lw=2, alpha=0.8)


print(thresholds)
print(computimes)

plt.figure(f0.number)
plt.title(plot_name + " performance")
plt.xlabel("p (%)")
plt.ylabel("Decoding success rate (%)")
plt.legend()

plt.figure(f1.number)
plt.title(plot_name + " computation time")
plt.xlabel("p (%)")
plt.ylabel("Time (s)")
plt.legend()
plt.show()


if save_result:
    fname = "./figures/" + file_name + "_thres_N" + str(Num) + ".pdf"
    f0.savefig(fname, transparent=True, format="pdf", bbox_inches="tight")
