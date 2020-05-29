'''
2020 Mark Shui Hu, QuTech

www.github.com/watermarkhu/oop_surface_code
_____________________________________________

'''
from thesis_style import *
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from collections import defaultdict
from scipy import optimize
import numpy as np
import math
import sys
sys.path.insert(0, '..')
from oopsc.threshold.fit import fit_thresholds, get_fit_func
from oopsc.threshold.sim import get_data, read_data




def plot(
    file_name,
    idx="",
    latts=[],
    probs=[],
    f0=None,                   # axis object of error fit plot
    lattices=None,
    ms=4,
    style="-",           # linestyles for data and fit
    plotn=1000,                  # number of points on x axis
    leg=False
):

    data = read_data(file_name)
    '''
    apply fit and get parameter
    '''
    (fitL, fitp, fitN, fitt), par = fit_thresholds(
        data, False, latts, probs)

    fit_func = get_fit_func(False)

    '''
    Plot and fit thresholds for a given dataset. Data is inputted as four lists for L, P, N and t.
    '''

    if f0 is None:
        f0, ax0 = plt.subplots()
    else:
        ax0 = f0.axes[0]

    LP = defaultdict(list)
    for L, P, N, T in zip(fitL, fitp, fitN, fitt):
        LP[L].append([P, N, T])

    if lattices is None:
        lattices = sorted(set(fitL))

    colors = {lati: f"C{i%10}" for i, lati in enumerate(lattices)}
    markerlist = get_markers()
    markers = {lati: markerlist[i % len(markerlist)]
               for i, lati in enumerate(lattices)}
    legend = []

    for i, lati in enumerate(lattices):
        fp, fN, fs = map(list, zip(*sorted(LP[lati], key=lambda k: k[0])))
        ft = [si / ni for si, ni in zip(fs, fN)]
        ax0.plot(
            [q for q in fp], ft, "x",
            color=colors[lati],
            marker=markers[lati],
            ms=ms,
            # ls="-",
            fillstyle="none",
        )
        X = np.linspace(min(fp), max(fp), plotn)
        ax0.plot(
            [x for x in X],
            [fit_func((x, lati), *par) for x in X],
            "-",
            color=colors[lati],
            lw=1.5,
            alpha=0.6,
            ls=style,
        )

        legend.append(Line2D(
            [0],
            [0],
            ls='None',
            label="{}".format(lati),
            color=colors[lati],
            marker=markers[lati],
            ms=ms,
            fillstyle="none"
        ))

    DS = fit_func((par[0], 20), *par)
    print("DS = {}".format(DS))

    # ax0.axvline(par[0] * 100, ls="dotted", color="k", alpha=0.5)
    pname = r"$p_{th}$"
    kname = r"$k_C$"
    # ax0.annotate(
    #     "{}= {}%, {} = {:.2f}".format(
    #         pname, str(round(100 * par[0], 2)), kname, DS),
    #     (par[0] * 100, DS),
    #     xytext=(10, 10),
    #     textcoords="offset points",
    #     fontsize=8,
    # )

    plot_style(ax0, "", r" $ p_X $", r"$k_C$")
    if leg:
        legend = plt.legend(handles=legend, loc="lower left", ncol=2,
                            markerscale=1, fontsize="small", columnspacing=0, labelspacing=0.2, handletextpad=0, numpoints=1)
        ax0.add_artist(legend)

    legend_entry = Line2D([0], [0], ls=style, color='k', label=idx)
    return f0, legend_entry

def plot_ufbb(
    file_name,
    idx="",
    latts=[],
    probs=[],
    lattices=None,
    ms=4,
    style="-",           # linestyles for data and fit
    plotn=1000,                  # number of points on x axis
):


    fit_func = get_fit_func(False)
    data = read_data(file_name)

    if not latts:
        latts = sorted(list(set(data.index.get_level_values("L"))))

    '''
    apply fit and get parameter
    '''
    parlist = []
    for i in range(len(latts)-1):
        (fitL, fitp, fitN, fitt), par = fit_thresholds(
            data, False, latts[i:i+2], probs)
        parlist.append(par)
    print("\nFinal:")
    (fitL, fitp, fitN, fitt), par = fit_thresholds(
        data, False, latts, probs)

    '''
    Plot and fit thresholds for a given dataset. Data is inputted as four lists for L, P, N and t.
    '''

    f0, ax0 = plt.subplots(tight_layout=True)
    f1, ax1 = plt.subplots(tight_layout=True)

    LP = defaultdict(list)
    for L, P, N, T in zip(fitL, fitp, fitN, fitt):
        LP[L].append([P, N, T])

    if lattices is None:
        lattices = sorted(set(fitL))

    colors = {lati: f"C{i%10}" for i, lati in enumerate(lattices)}
    markerlist = get_markers()
    markers = {lati: markerlist[i % len(markerlist)]
                for i, lati in enumerate(lattices)}

    leg1, leg2 = [], []

    for i, lati in enumerate(lattices):
        fp, fN, fs = map(list, zip(*sorted(LP[lati], key=lambda k: k[0])))
        ft = [si / ni for si, ni in zip(fs, fN)]
        ax0.plot(
            [q for q in fp], ft,
            color=colors[lati],
            ls="-",
            lw=1,
            alpha=0.5,
        )
        ax0.plot(
            [q for q in fp], ft, "x",
            color=colors[lati],
            marker=markers[lati],
            ms=ms,
            fillstyle="none",
        )
        leg1.append(Line2D(
            [0],
            [0],
            ls='None',
            label="{}".format(lati),
            color=colors[lati],
            marker=markers[lati],
            ms=ms,
            fillstyle="none"
        ))

    DS = fit_func((par[0], 20), *par)
    print("DS = {}".format(DS))

    var= 0.0004
    for par, lati, laty in zip(parlist, latts[:-1], latts[1:]):

        X = np.linspace(par[0] - var, par[0] + var, plotn)
        ax1.plot(
            [x for x in X],
            [fit_func((x, lati), *par) for x in X],
            "-",
            color=colors[lati],
            lw=1,
            alpha=0.5,
            ls=style,
        )
        ax1.plot(
            [x for x in X],
            [fit_func((x, laty), *par) for x in X],
            "-",
            color=colors[laty],
            lw=1,
            alpha=0.5,
            ls=style,
        )
        leg2.append(Line2D(
            [0],
            [0],
            ls='None',
            label=f"{lati},{laty}",
            color=colors[lati],
            marker=markers[laty],
            ms=ms,
        ))
    thresholds = []
    for par, lati, laty in zip(parlist, latts[:-1], latts[1:]):
        pth = par[0]
        kc = fit_func((pth, 20), *par)
        thresholds.append([pth, kc, colors[lati], markers[laty]])
        plt.plot(pth, kc, color=colors[lati],
                 marker=markers[laty], ms=ms)


    pname = r"$p_{th}$"
    kname = r"$k_C$"

    plot_style(ax0, "", r" $ p_X $", r"$k_C$")
    ax0.legend(handles=leg1, loc="lower left", ncol=2, **legend_style())
    plot_style(ax1, "", r" $ p_X $", r"$k_C$")
    ax1.legend(handles=leg2, loc="upper right", ncol=2, **legend_style())

    return f0, f1, thresholds



def plot_multiple(locs, names=None, styles=["-"], showleg=True, **kwargs):

    f, ax = plt.subplots(tight_layout=True)

    if names == None:
        names = [""]*len(locs)
        showleg = False 

    artists = []
    for (loc, name, style) in zip(locs, names, styles):
        data = "/home/watermarkhu/mep/oop_surface_code/cartesiusdata/{}.csv".format(loc)
        if style == "-":
            f, leg = plot(data, idx=name, style=style, leg=True, f0=f, **kwargs)
        else:
            f, leg = plot(data, idx=name, style=style, f0=f, **kwargs)
        artists.append(leg)

    if showleg:
        legend = plt.legend(handles=artists, loc="upper right")
        ax.add_artist(legend)

    return f, ax

