from thesis_style import *
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from collections import defaultdict
from scipy import optimize
import numpy as np
import math
import sys
sys.path.insert(0, '..')
from simulator.threshold.fit import fit_thresholds, get_fit_func
from simulator.threshold.sim import get_data, read_data



def plot(
    file_name,
    title="",
    idx="",
    latts=[],
    probs=[],
    modified_ansatz=False,
    ax=None,                   # axis object of error fit plot
    ms=3,
    lw=1,
    mew=1,
    style="-",           # linestyles for data and fit
    leg=False,
    legendname="",
    legloc="lower left",
    yb=False,
    starti=0,
    **kwargs
):

    data = read_data(file_name)
    '''
    apply fit and get parameter
    '''
    (fitL, fitp, fitN, fitt), par = fit_thresholds(
        data, modified_ansatz, latts, probs)

    fit_func = get_fit_func(modified_ansatz)

    '''
    Plot and fit thresholds for a given dataset. Data is inputted as four lists for L, P, N and t.
    '''

    LP = defaultdict(list)
    for L, P, N, T in zip(fitL, fitp, fitN, fitt):
        LP[L].append([P, N, T])

    lattices = sorted(set(fitL))

    colors = {lati: f"C{(i+starti)%10}" for i, lati in enumerate(lattices)}
    markerlist = get_markers()
    markers = {lati: markerlist[(i+starti) % len(markerlist)]
               for i, lati in enumerate(lattices)}
    legend = []

    for i, lati in enumerate(lattices):
        fp, fN, fs = map(list, zip(*sorted(LP[lati], key=lambda k: k[0])))
        ft = [si / ni for si, ni in zip(fs, fN)]
        ax.plot(
            [q for q in fp], ft,
            color=colors[lati],
            ls=style,
            lw=lw,
            marker=markers[lati],
            mew=mew,
            ms=ms,
            fillstyle="none",
        )
        legend.append(Line2D(
            [0],
            [0],
            ls='None',
            label="{}".format(lati),
            color=colors[lati],
            marker=markers[lati],
            mew=mew,
            ms=ms,
            lw=lw,
            fillstyle="none"
        ))

    DS = fit_func((par[0], 20), *par)
    print("DS = {}".format(DS))

    pname = r"$p_{th}$"
    kname = r"$k_C$"

    if yb:
        plot_style(ax, title, r"$p_X $", r"$k_C$", **kwargs)
    else:
        plot_style(ax, title, r"$p_X $", "", **kwargs)

    if leg:
        legend = ax.legend(handles=legend, loc=legloc, ncol=2,
                            markerscale=1, fontsize="small", columnspacing=0, labelspacing=0.2, handletextpad=0, numpoints=1, title=r"{}$L$".format(legendname), title_fontsize=8)

    return ax


if __name__ == "__main__":
    latex_style(1, 0.4)
    (f1, axes1) = plt.subplots(1, 4, sharey=True, tight_layout=True)
    (f2, axes2) = plt.subplots(1, 4, sharey=True, tight_layout=True)

    D2 = [
        "/home/watermarkhu/mep/OpenSurfaceSim/cartesiusdata/delfosse_2d_uf.csv",
        "/home/watermarkhu/mep/OpenSurfaceSim/cartesiusdata/delfosse_2d_dbuf.csv",
        "/home/watermarkhu/mep/OpenSurfaceSim/cartesiusdata/delfosse_2d_ufbb.csv",
        "/home/watermarkhu/mep/OpenSurfaceSim/cartesiusdata/delfosse_2d_mwpm.csv",
    ]

    D3 = [
        "/home/watermarkhu/mep/OpenSurfaceSim/cartesiusdata/delfosse_3d_uf.csv",
        "/home/watermarkhu/mep/OpenSurfaceSim/cartesiusdata/delfosse_3d_dbuf.csv",
        "/home/watermarkhu/mep/OpenSurfaceSim/cartesiusdata/delfosse_3d_ufbb.csv",
        "/home/watermarkhu/mep/OpenSurfaceSim/cartesiusdata/delfosse_3d_mwpm.csv",
    ]
        
    plot(D2[0], "Union-Find", ax=axes1[0], yb=1)
    plot(D3[0], "Union-Find", ax=axes2[0], yb=1)
    plot(D2[1], "DBUF", ax=axes1[1])
    plot(D3[1], "DBUF", ax=axes2[1])
    plot(D2[2], "UFBB", ax=axes1[2])
    plot(D3[2], "UFBB", ax=axes2[2])
    plot(D2[3], "MWPM", ax=axes1[3], leg=1)
    plot(D3[3], "MWPM", ax=axes2[3], leg=1)

    plt.show()

    f1.savefig("/home/watermarkhu/mep/mep-thesis/pgfplots/threshold_delfosse_2d.pgf")
    f2.savefig("/home/watermarkhu/mep/mep-thesis/pgfplots/threshold_delfosse_3d.pgf")
