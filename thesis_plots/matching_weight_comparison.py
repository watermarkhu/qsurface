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
from oopsc.threshold.fit import fit_thresholds, get_fit_func
from oopsc.threshold.sim import get_data, read_data


def plot_style(ax, title=None, xlabel=None, ylabel=None, **kwargs):
    ax.grid(color='w', linestyle='-', linewidth=2)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    for key, arg in kwargs.items():
        func = getattr(ax, f"set_{key}")
        func(arg)
    ax.patch.set_facecolor('0.95')
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.spines["left"].set_visible(False)


def get_markers():
    return ["o", "s", "v", "D", "p", "^", "h", "X", "<", "P", "*", ">", "H", "d", 4, 5, 6, 7, 8, 9, 10, 11]


def get_colors():
    return {
        "UF-xW-xDF":    "C0",
        "UF-W-xDF":     "C1",   
        "UF-xW-DF":     "C2",
        "UF-W-DF":      "C3",
        "MWPM":         "C4",
        "UF-BB":        "C8",
    }

def get_linestyles():
     return {
        "UF-xW-xDF":    "--",
        "UF-W-xDF":     ":",   
        "UF-xW-DF":     "-.",
        "UF-W-DF":      (0, (5, 1)),
        "MWPM":         "-",
        "UF-BB":        (0, (3, 1, 1, 1, 1, 1)),
    }


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

            if name == "MWPM":
                ylabel = 0.1

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
    # L2 = plt.legend(handles=leg2, loc="upper left", ncol=3)
    # plt.gca().add_artist(L2)

    plot_style(plt.gca(), "Comparison of {}".format(
        feature), xchoice, "{} count".format(feature))
    plt.title("Comparison of matching weight")

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

            if i == 0:
                ylabel = 0.1

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
                continue
            else:
                Y = [y1-y2 for y1, y2 in zip(Y,Ynorm)]

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
    # L2 = plt.legend(handles=leg2, loc="upper left", ncol=3)
    # plt.gca().add_artist(L2)

    plot_style(plt.gca(), "Comparison of {}".format(
        feature), xchoice, "{} count".format(feature))
    plt.title("Comparison of matching weight, normalized to MWPM")

    plt.show()



l = [8+i*8 for i in range(8)]

names = [
    "../cartesiusdata/data/ufndfuwg_toric_2d.csv",
    "../cartesiusdata/data/ufndf_toric_2d.csv",
    "../cartesiusdata/data/ufuwg_toric_2d.csv",
    "../cartesiusdata/data/uf_toric_2d.csv",
    "../cartesiusdata/data/mwpm_toric_2d.csv"
]
plot_compare(["UF-xW-xDF", "UF-W-xDF", "UF-xW-DF", "UF-W-DF", "MWPM"], names, "l", [0.098], l, "weight", dim=2)
names = [
    "../cartesiusdata/data/mwpm_toric_2d.csv",
    "../cartesiusdata/data/ufndfuwg_toric_2d.csv",
    "../cartesiusdata/data/ufndf_toric_2d.csv",
    "../cartesiusdata/data/ufuwg_toric_2d.csv",
    "../cartesiusdata/data/uf_toric_2d.csv",
]
plot_compare2(["MWPM", "UF-xW-xDF", "UF-W-xDF", "UF-xW-DF", "UF-W-DF"], names, "l", [0.098], l, "weight", dim=2)

names = [
    "../cartesiusdata/data/uf_toric_2d.csv",
    "../cartesiusdata/data/eg_toric_2d.csv",
    "../cartesiusdata/data/mwpm_toric_2d.csv"
]
plot_compare(["UF-W-DF","UF-BB","MWPM"], names, "l", [0.098], l, "weight", dim=2)


names = [
    "../cartesiusdata/data/mwpm_toric_2d.csv",
    "../cartesiusdata/data/uf_toric_2d.csv",
    "../cartesiusdata/data/eg_toric_2d.csv",
]
plot_compare2(["MWPM", "UF-W-DF", "UF-BB"],
              names, "l", [0.098], l, "weight", dim=2)


names = [
    "../cartesiusdata/data/mwpm_toric_2d.csv",
    "../cartesiusdata/data/ufndfuwg_toric_2d.csv",
    "../cartesiusdata/data/ufndf_toric_2d.csv",
    "../cartesiusdata/data/ufuwg_toric_2d.csv",
    "../cartesiusdata/data/uf_toric_2d.csv",
    "../cartesiusdata/data/eg_toric_2d.csv",
]
plot_compare2(["MWPM", "UF-xW-xDF", "UF-W-xDF", "UF-xW-DF", "UF-W-DF", "UF-BB"],
              names, "l", [0.098], l, "weight", dim=2)
