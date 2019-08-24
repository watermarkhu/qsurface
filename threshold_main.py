from matplotlib import pyplot as plt
from run_toric_2D_uf import multiprocess
import numpy as np
import pandas as pd
import datetime
import time

if __name__ == '__main__':

    save_result = 0

    folder = "../../../OneDrive - Delft University of Technology/MEP - thesis Mark/Simulations/"

    file_name = "peeling_toric_pX_bucketC_ao=rand_rt=on"
    plot_name = "Peeling decoder (toric) vs. Pauli X error rate (bucket_C, ao=rand, rt=on)"

    lattices = [8]
    p = list(np.linspace(0.09, 0.11, 11))
    Num = 10000
    plotn = 1000

    ### Code ###

    st = datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d')[2:]
    thresholds = np.zeros((len(lattices), len(p)))
    X = np.linspace(p[0], p[-1], plotn)
    f0 = plt.figure()


    for i, lati in enumerate(lattices):
        for j, pi in enumerate(p):

            print("Calculating for L = ", str(lati), "and p =", str(pi))
            N_succes = multiprocess(lati, Num, 0, pi, 0, processes=4)
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
    plt.xlabel("probability of Pauli X error (%)")
    plt.ylabel("decoding success rate (%)")
    plt.legend()

    if save_result:
        data.to_csv(folder + "data/" + st + "_" + file_name + "_N" + str(Num) + ".csv")
        fname = folder + "./figures/" + st + "_" + file_name + "_N" + str(Num) + ".pdf"
        f0.savefig(fname, transparent=True, format="pdf", bbox_inches="tight")
