from thesis_style import *
import sys
sys.path.insert(0, '..')

from collections import defaultdict
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import numpy as np
from oopsc.threshold.sim import get_data, read_data
from oopsc.threshold.fit import get_fit_func, fit_thresholds


def plot_thresholds(
    data,
    color,
    height,
    modified_ansatz=False,
    latts=[],
    probs=[],
    ax0=None,                   # axis object of error fit plot
    par=None,
    lattices=None,
    ms=5,
):

    styles=[".", "-"]           # linestyles for data and fit
    plotn=1000                  # number of points on x axis

    '''
    apply fit and get parameter
    '''
    if par is None:
        (fitL, fitp, fitN, fitt), par = fit_thresholds(data, modified_ansatz, latts, probs)
    else:
        fitL, fitp, fitN, fitt = get_data(data, latts, probs)


    fit_func = get_fit_func(modified_ansatz)

    '''
    Plot and fit thresholds for a given dataset. Data is inputted as four lists for L, P, N and t.
    '''

    if ax0 is None:
        f0, ax0 = plt.subplots()

    LP = defaultdict(list)
    for L, P, N, T in zip(fitL, fitp, fitN, fitt):
        LP[L].append([P, N, T])

    if lattices is None:
        lattices = sorted(set(fitL))

    markerlist = get_markers()
    markers = {lati: markerlist[i%len(markerlist)] for i, lati in enumerate(lattices)}


    for i, lati in enumerate(lattices):
        fp, fN, fs = map(list, zip(*sorted(LP[lati], key=lambda k: k[0])))
        ft = [si / ni for si, ni in zip(fs, fN)]
        ax0.plot(
            [q for q in fp], ft, styles[0],
            color=color,
            marker=markers[lati],
            ms=ms,
            fillstyle="none",
            alpha=0.3
        )
        X = np.linspace(min(fp), max(fp), plotn)

    xval = [x for x in X]
    y1 = [fit_func((x, lattices[0]), *par) for x in X]
    y2 = [fit_func((x, lattices[-1]), *par) for x in X]


def comp_thresholds(Lrange, type, decoders=[], thdata=[]):

    f, ax = plt.subplots()

    colordict = get_colors()
    legend_elements = []

    for decoder in decoders:
        color = colordict[decoder]
        data = read_data("../cartesiusdata/{}_{}.csv".format(decoder.lower(), type))
        plot_thresholds(data, color, 0.65, ax0=ax, latts=Lrange)
        legend_elements.append(Patch(facecolor=color, label=decoder, alpha=0.2))
    

    for i, (x, y, color, marker) in enumerate(thdata):
        plt.plot(x, y, "*", ms=5, color=color, marker=marker)

    plot_style(ax, "", r" $ p_X $", r"$k_C$")

    markerlist = get_markers()
    markers = {lati: markerlist[i%len(markerlist)] for i, lati in enumerate(Lrange)}
    legend = []
    for lati in Lrange:
        legend.append(Line2D(
            [0],
            [0],
            label="{}".format(lati),
            marker=markers[lati],
            ms=5,
            fillstyle="none",
            linewidth=0,
            color="k"
        ))

    ax.add_artist(plt.legend(handles=legend, ncol=2, loc="lower left", **legend_style()))
    ax.add_artist(plt.legend(handles=legend_elements, loc="upper right"))

    return f


if __name__ == "__main__":

    comp_thresholds([8+8*i for i in range(8)], "toric_2d",  decoders=["SUF", "DUF", "SBUF", "DBUF", "MWPM"])
    comp_thresholds([8+8*i for i in range(8)], "planar_2d", decoders=["SUF", "DUF", "SBUF", "DBUF", "MWPM"])
    comp_thresholds([8+4*i for i in range(8)], "toric_3d",  decoders=["SUF", "DUF", "SBUF", "DBUF", "MWPM"])
    comp_thresholds([8+4*i for i in range(8)], "planar_3d", decoders=["SUF", "DUF", "SBUF", "DBUF", "MWPM"])
    comp_thresholds([8+8*i for i in range(8)], "toric_2d",  decoders=["DBUF", "MWPM", "UFBB"])
    comp_thresholds([8+8*i for i in range(8)], "planar_2d", decoders=["DBUF", "MWPM", "UFBB"])
    comp_thresholds([8+4*i for i in range(8)], "toric_3d",  decoders=["DBUF", "MWPM", "UFBB"])
    comp_thresholds([8+4*i for i in range(8)], "planar_3d", decoders=["DBUF", "MWPM", "UFBB"])
    plt.show()