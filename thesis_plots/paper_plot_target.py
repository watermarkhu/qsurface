#%%
from thesis_style import *
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from collections import defaultdict
from scipy import optimize
import numpy as np
import math
import sys
sys.path.insert(0, '..')
from simulator.threshold.sim import get_data, read_data
from simulator.threshold.fit import fit_thresholds, get_fit_func



#%%
sims = ["mwpm_toric_2d", "dbuf_toric_2d", "ufbb_toric_2d"]

for sim in sims:
    folder = "~/mep/OpenSurfaceSim/cartesius/data/"
    data = read_data(folder + sim + ".csv")
    rates = np.linspace(0.5, 1, 101)


    #%%
    lattices = sorted(list(set(data.index.get_level_values("L"))))
    pdata, cdata, fdata = [], [], []
    for l in lattices:
        ld = data.query("L==@l")
        p = list(ld.index.droplevel(0))
        c = [s/n for s, n in zip(ld["succes"], ld["N"])]
        f = np.polyfit(p, c, 2)

        pdata.append(p)
        cdata.append(c)
        fdata.append(f)

    plt.figure()
    for i, (p,c,f, l) in enumerate(zip(pdata,cdata,fdata,lattices)):
        plt.plot(p, c, 'x', color="C{:02d}".format(i), label=l)
        x = np.linspace(min(p), max(p), 1000)
        plt.plot(x, np.poly1d(f)(x))
    plt.legend()
        #%%

    def solvey(y, a, b, c):
        c -=  y
        D = b**2 - 4*a*c
        x = (- b - D**(1/2)) / (2*a)
        return x

    plt.figure()
    for rate in rates:
        L, k = [], []
        for c,f,l in zip(cdata, fdata, lattices):
            if rate > min(c) and rate < max(c):
                L.append(l)
                k.append(solvey(rate, *f))
        if L:
            plt.plot(k, L, "k-")
    plt.xlabel("p")
    plt.ylabel("L")

    # %%
plt.show()
