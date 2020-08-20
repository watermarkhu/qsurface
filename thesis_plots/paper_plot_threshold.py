import sys
sys.path.insert(0, '..')

from collections import defaultdict
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import numpy as np
from simulator.threshold.sim import get_data, read_data
from simulator.threshold.fit import get_fit_func, fit_thresholds


def plot_style(ax, title=None, xlabel=None, ylabel=None, **kwargs):
    ax.grid(linestyle=':', linewidth=.5)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    for key, arg in kwargs.items():
        func = getattr(ax, f"set_{key}")
        func(arg)
    # ax.patch.set_facecolor('0.95')
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.spines["left"].set_visible(False)

def get_markers():
    return ["o", "*", "v", ">", "<", "^", "h", "X", "<", "P", "*", ">", "H", "d", 4, 5, 6, 7, 8, 9, 10, 11]


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
            [q * 100 for q in fp], ft, styles[0],
            color=color,
            marker=markers[lati],
            ms=ms,
            fillstyle="none",
        )
        X = np.linspace(min(fp), max(fp), plotn)

    xval = [x * 100 for x in X]
    y1 = [fit_func((x, lattices[0]), *par) for x in X]
    y2 = [fit_func((x, lattices[-1]), *par) for x in X]

    ax0.fill_between(xval,y1,y2, facecolor=color, alpha=0.3)

    # ax0.axvline(par[0] * 100, ls="dotted", color="k", alpha=0.5)
    # ax0.annotate(
    #     "{}%".format(str(round(100 * par[0], 2))),
    #     (par[0] * 100 - 0.02, height),
    #     xytext=(10, 10),
    #     textcoords="offset points",
    #     fontsize=12,
    # )


f, ax = plt.subplots()
SMALL_SIZE = 13
MEDIUM_SIZE = 16
BIGGER_SIZE = 14

plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
plt.rc('axes', titlesize=SMALL_SIZE)     # fontsize of the axes title
plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('legend', fontsize=SMALL_SIZE)    # legend fontsize
plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title

Lrange = [8, 16, 24, 32, 40, 48]
mwdata = read_data("../cartesiusdata/mwpm_toric_2d.csv")
plot_thresholds(mwdata, "C3", 0.65, ax0=ax, latts=Lrange)
ufdata = read_data("../cartesiusdata/dbuf_toric_2d.csv")
plot_thresholds(ufdata, "C0", 0.65, ax0=ax, latts=Lrange)
bbdata = read_data("../cartesiusdata/ufbb_toric_2d.csv")
plot_thresholds(bbdata, "C2", 0.640, ax0=ax, latts=Lrange, probs=[round(0.099 + i*0.0005, 5) for i in range(11)])
plot_style(ax, "", "Probability of Pauli X error (%)", "Decoding success rate")


# Lrange = [8, 12, 16, 20]
# mwdata = read_data("../cartesiusdata/mwpm_toric_3d.csv")
# plot_thresholds(mwdata, "C3", 0.78, ax0=ax, latts=Lrange)
# ufdata = read_data("../cartesiusdata/dbuf_toric_3d.csv")
# plot_thresholds(ufdata, "C0", 0.78, ax0=ax, latts=Lrange)
# bbdata = read_data("../cartesiusdata/eg_toric_3d.csv")
# plot_thresholds(bbdata, "C2", 0.78, ax0=ax, latts=Lrange, probs=[round(0.027 + i*0.001/3, 5) for i in range(10)])
# plot_style(ax, "", "Probability of Pauli X error (%)", "Decoding success rate")


markerlist = get_markers()
markers = {lati: markerlist[i%len(markerlist)] for i, lati in enumerate(Lrange)}
legend = []
for lati in Lrange:
    legend.append(Line2D(
        [0],
        [0],
        label="L = {}".format(lati),
        marker=markers[lati],
        ms=5,
        fillstyle="none",
        linewidth=0,
        color="k"
    ))
legend_elements = [
    Patch(facecolor="C3", label='MWPM', alpha=0.8),
    Patch(facecolor="C0", label='UF', alpha=0.8),
    Patch(facecolor="C2", label='UFBB', alpha=0.8),
]

ax.add_artist(plt.legend(handles=legend, loc="upper right"))
ax.add_artist(plt.legend(handles=legend_elements, loc="lower left"))

plt.title("Threshold")
plt.show()
# f.savefig("threshold.pdf", transparent=True, format="pdf")
