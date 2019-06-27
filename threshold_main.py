import run_multiple
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import datetime
import time

save_result = True

file_name = "peeling_toric_only_pX_bucket_ncount"
plot_name = "Peeling decoder toric lattice with only Pauli error - bucket, ncount"

lattices = [8, 12, 16, 20]
p = list(np.linspace(0.09, 0.11, 11))
Num = 30000
plotn = 500

### Code ###

st = datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d')[2:]
thresholds = np.zeros((len(lattices), len(p)))
X = np.linspace(p[0], p[-1], plotn)
f0 = plt.figure()

for i, lati in enumerate(lattices):
    for j, pi in enumerate(p):

        print("Calculating for L = ", str(lati), "and p =", str(pi))
        N_succes = run_multiple.toric_2D_peeling(lati, 0, pi, 0, Num, plot_load=False)
        thresholds[i, j] = N_succes / Num * 100

    plt.figure(f0.number)
    fit = np.polyfit(p, thresholds[i, :], 2)
    polyfit = np.poly1d(fit)
    plt.plot([q*100 for q in p], thresholds[i, :], '.', color='C'+str(i), ms=10)
    plt.plot([x*100 for x in X], polyfit(X), '-', label=lati, color='C'+str(i), lw=2, alpha=0.8)

data = pd.DataFrame(data=thresholds, index=lattices, columns=p)
print(data)

plt.figure(f0.number)
plt.title(plot_name + " performance")
plt.xlabel("p (%)")
plt.ylabel("Decoding success rate (%)")
plt.legend()

if save_result:
    data.to_csv("./data/" + st + file_name + "_N" + str(Num) + ".csv")
    fname = "./figures/" + st + file_name + "_N" + str(Num) + ".pdf"
    f0.savefig(fname, transparent=True, format="pdf", bbox_inches="tight")
