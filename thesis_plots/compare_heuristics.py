'''
2020 Mark Shui Hu, QuTech

www.github.com/watermarkhu/oop_surface_code
_____________________________________________

'''
import sys
sys.path.insert(0, '..')

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from collections import defaultdict
from scipy import optimize
import numpy as np
import math
from simulator.threshold.fit import fit_thresholds, get_fit_func
from simulator.threshold.sim import get_data, read_data

from thesis_style import *


def get_csvdir(names):
    return ["../cartesiusdata/{}.csv".format(n) for n in names]


def plot_compare(
    names,
    csv_names, 
    xaxis, 
    probs, 
    latts, 
    feature, 
    plot_error=False, 
    dim=1,
    xm=1, 
    ms=5,
    normy=None,
    yname="",
    output="", 
    fitname="", 
    **kwargs
    ):

    if fitname == "":
        fit = None
    else:
        if fitname in globals():
            fit = globals()[fitname]()
        else:
            print("fit does not exist")
            fit = None

    markers = get_markers()
    colors = get_colors()
    linestyles = get_linestyles()


    xchoice = dict(p="p", P="p", l="L", L="L")
    ychoice = dict(p="L", P="L", l="p", L="p")
    xchoice, ychoice = xchoice[xaxis], ychoice[xaxis]
    xlabels, ylabels = (probs, latts) if xaxis == "p" else (latts, probs)
    if xlabels:
        xlabels = sorted(xlabels)


    data, leg1, leg2 = [], [], []
    for i, (name, x) in enumerate(zip(csv_names, names)):
        ls = linestyles[x]
        leg1.append(Line2D([0], [0], ls=ls,  color=colors[x], label=x))
        data.append(read_data(name))

    if not ylabels:
        ylabels = set()
        for df in data:
            for item in df.index.get_level_values(ychoice):
                ylabels.add(round(item, 6))
        ylabels = sorted(list(ylabels))

    xset = set()
    for i, (df,name) in enumerate(zip(data,names)):

        indices = [round(x, 6) for x in df.index.get_level_values(ychoice)]
        ls = linestyles[name]

        for j, ylabel in enumerate(ylabels):

            marker = markers[i % len(markers)]
            # color = colors[ylabel]
            color = colors[name]

            if name == "MWPM" and normy is not None:
                ylabel = normy

            d = df.loc[[x == ylabel for x in indices]]
            index = [round(v, 6) for v in d.index.get_level_values(xchoice)]
            d = d.reset_index(drop=True)
            d["index"] = index
            d = d.set_index("index")

            if not xlabels:
                X = index
                xset = xset.union(set(X))
            else:
                X = [x for x in xlabels if x in d.index.values]

            column = feature if feature in df else f"{feature}_m"
            Y = [d.loc[x, column] for x in X]

            if dim != 1:
                X = [x**dim for x in X]

            # print(ylabel, X, Y)
            #
            if fit is not None:
                guess, min, max = fit.guesses()
                res = optimize.curve_fit(
                    fit.func, X, Y, guess, bounds=[min, max])
                step = abs(int((X[-1] - X[0])/100))
                pn = np.array(range(X[0], X[-1] + step, step))
                ft = fit.func(pn, *res[0])
                plt.plot(pn, ft, ls=ls, c=color)
                plt.plot(X, Y, lw=0, c=color, marker=marker,
                         ms=ms, fillstyle="none")
                print(f"{ychoice} = {ylabel}", fit.show(*res[0]))
            else:
                plt.plot(X, Y, ls=ls, c=color, marker=marker,
                         ms=ms, fillstyle="none")

            if i == 0:
                leg2.append(Line2D([0], [0], ls=ls, c=color, marker=marker,
                                   ms=ms, fillstyle="none", label=f"{ychoice}={ylabel}"))

            if plot_error and f"{feature}_v" in d:
                E = list(d.loc[:, f"{feature}_v"])
                ym = [y - e for y, e in zip(Y, E)]
                yp = [y + e for y, e in zip(Y, E)]
                plt.fill_between(X, ym, yp, alpha=0.1,
                                 facecolor=color, edgecolor=color, ls=ls, lw=2)

    xnames = sorted(list(xset)) if not xlabels else xlabels
    xticks = [x**dim for x in xnames]
    xnames = [round(x*xm, 3) for x in xnames]

    plt.xticks(xticks, xnames)
    L1 = plt.legend(handles=leg1, loc="upper left")
    plt.gca().add_artist(L1)
    if len(probs) > 1:
        L2 = plt.legend(handles=leg2, loc="upper left", ncol=3)
        plt.gca().add_artist(L2)

    plot_style(plt.gca(), "", xchoice, yname)
    # plt.title("Comparison of matching weight")
    plt.tight_layout()

    if output:
        plt.savefig("/home/watermarkhu/mep/mep-thesis/pgfplots/{}.pgf".format(output))
    plt.show()


def plot_compare2(
    names,
    csv_names,
    xaxis,
    probs,
    latts,
    feature,
    plot_error=False,
    dim=1,
    xm=1,
    ms=5,
    normy=None,
    yname="",
    output="",
    fitname="",
    **kwargs
):

    if fitname == "":
        fit = None
    else:
        if fitname in globals():
            fit = globals()[fitname]()
        else:
            print("fit does not exist")
            fit = None

    markers = get_markers()
    colors = get_colors()
    linestyles = get_linestyles()


    xchoice = dict(p="p", P="p", l="L", L="L")
    ychoice = dict(p="L", P="L", l="p", L="p")
    xchoice, ychoice = xchoice[xaxis], ychoice[xaxis]
    xlabels, ylabels = (probs, latts) if xaxis == "p" else (latts, probs)
    if xlabels:
        xlabels = sorted(xlabels)


    data, leg1, leg2 = [], [], []
    for i, (name, x) in enumerate(zip(csv_names, names)):
        data.append(read_data(name))
        if i != 0:
            ls = linestyles[x]
            leg1.append(Line2D([0], [0], ls=ls,  color=colors[x], label=x))

    if not ylabels:
        ylabels = set()
        for df in data:
            for item in df.index.get_level_values(ychoice):
                ylabels.add(round(item, 6))
        ylabels = sorted(list(ylabels))


    xset = set()
    for i, (df, name) in enumerate(zip(data, names)):

        indices = [round(x, 6) for x in df.index.get_level_values(ychoice)]
        ls = linestyles[name]

        for j, ylabel in enumerate(ylabels):

            marker = markers[i-1 % len(markers)]
            # color = colors[ylabel]
            color = colors[name]

            if i == 0 and normy is not None:
                ylabel = normy

            d = df.loc[[x == ylabel for x in indices]]
            index = [round(v, 6) for v in d.index.get_level_values(xchoice)]
            d = d.reset_index(drop=True)
            d["index"] = index
            d = d.set_index("index")

            if not xlabels:
                X = index
                xset = xset.union(set(X))
            else:
                X = [x for x in xlabels if x in d.index.values]

            column = feature if feature in df else f"{feature}_m"
            Y = [d.loc[x, column] for x in X]

            if dim != 1:
                X = [x**dim for x in X]

            if i == 0:
                Ynorm = Y
                marker="None"

            Y = [y1/y2 for y1, y2 in zip(Y,Ynorm)]

            # print(ylabel, X, Y)
            #
            if fit is not None:
                guess, min, max = fit.guesses()
                res = optimize.curve_fit(
                    fit.func, X, Y, guess, bounds=[min, max])
                step = abs(int((X[-1] - X[0])/100))
                pn = np.array(range(X[0], X[-1] + step, step))
                ft = fit.func(pn, *res[0])
                plt.plot(pn, ft, ls=ls, c=color)
                plt.plot(X, Y, lw=0, c=color, marker=marker,
                         ms=ms, fillstyle="none")
                print(f"{ychoice} = {ylabel}", fit.show(*res[0]))
            else:
                plt.plot(X, Y, ls=ls, c=color, marker=marker,
                         ms=ms, fillstyle="none")

            if i == 0:
                leg2.append(Line2D([0], [0], ls=ls, c=color, marker=marker,
                                   ms=ms, fillstyle="none", label=f"{ychoice}={ylabel}"))

            if plot_error and f"{feature}_v" in d:
                E = list(d.loc[:, f"{feature}_v"])
                ym = [y - e for y, e in zip(Y, E)]
                yp = [y + e for y, e in zip(Y, E)]
                plt.fill_between(X, ym, yp, alpha=0.1,
                                 facecolor=color, edgecolor=color, ls=ls, lw=2)

    xnames = sorted(list(xset)) if not xlabels else xlabels
    xticks = [x**dim for x in xnames]
    xnames = [round(x*xm, 3) for x in xnames]

    plt.xticks(xticks, xnames)
    L1 = plt.legend(handles=leg1) #, loc="center right", bbox_to_anchor=(1, 0.2))
    plt.gca().add_artist(L1)

    if len(probs) > 1:
        L2 = plt.legend(handles=leg2, ncol=3)
        plt.gca().add_artist(L2)

    plot_style(plt.gca(), "", xchoice, yname)
    # plt.title("Comparison of matching weight, normalized to MWPM")
    plt.tight_layout()
    if output:
        plt.savefig("/home/watermarkhu/mep/mep-thesis/pgfplots/{}.pgf".format(output))
    plt.show()





# names = [
#     "data/uf_toric_2d",
#     "data/ufbb_toric_2d",
#     "data/mwpm_toric_2d"
# ]
# plot_compare(["DBUF","UF-BB","MWPM"], names, "l", [0.098], l, "weight", dim=2)


# names = [
#     "data/mwpm_toric_2d",
#     "data/uf_toric_2d",
#     "data/ufbb_toric_2d",
# ]
# plot_compare2(["MWPM", "DBUF", "UF-BB"],
#               names, "l", [0.098], l, "weight", dim=2)


# names = [
#     "data/mwpm_toric_2d",
#     "data/suf_toric_2d",
#     "data/duf_toric_2d",
#     "data/sbuf_toric_2d",
#     "data/uf_toric_2d",
#     "data/ufbb_toric_2d",
# ]
# plot_compare2(["MWPM", "SUF", "DUF", "SBUF", "DBUF", "UF-BB"],
#               names, "l", [0.098], l, "weight", dim=2)

