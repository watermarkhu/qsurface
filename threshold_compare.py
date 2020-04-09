'''
2020 Mark Shui Hu, QuTech

www.github.com/watermarkhu/oop_surface_code
_____________________________________________
'''

import matplotlib.pyplot as plt
from threshold_fit import read_data
from matplotlib.lines import Line2D
from threshold_plot import plot_style, get_markers
from scipy import optimize
import numpy as np
import math


class npolylogn(object):
    def func(self, N, A, B, C):
        return A*N*(np.log(N)/math.log(B))**C

    def guesses(self):
        guess = [0.01, 10, 1]
        min = (0, 1, 1)
        max = (1, 1000000, 100)
        return guess, min, max

    def show(self, *args):
        return f"n*(log_A(n))**B with A={round(args[1], 5)}, B={round(args[2], 5)}"


class linear(object):
    def func(self, N, A, B):
        return A*N+B

    def guesses(self):
        guess = [0.01, 10]
        min = (0, 0)
        max = (10, 1000)
        return guess, min, max

    def show(self, *args):
        return f"A*n with A={round(args[0], 6)}"


class nlogn(object):
    def func(self, N, A, B):
        return A*N*(np.log(N)/math.log(B))

    def guesses(self):
        guess = [0.01, 10]
        min = (0, 1)
        max = (1, 1000000)
        return guess, min, max

    def show(self, *args):
        return f"n*(log_A(n)) with A={round(args[1], 5)}"


def plot_compare(csv_names, xaxis, probs, latts, feature, plot_error, dim, xm, ms, output, fitname, **kwargs):

    if fitname == "":
        fit = None
    else:
        if fitname in globals():
            fit = globals()[fitname]()
        else:
            print("fit does not exist")
            fit=None

    markers = get_markers()

    xchoice = dict(p="p", P="p", l="L", L="L")
    ychoice = dict(p="L", P="L", l="p", L="p")
    xchoice, ychoice = xchoice[xaxis], ychoice[xaxis]
    xlabels, ylabels = (probs, latts) if xaxis == "p" else (latts, probs)
    if xlabels: xlabels = sorted(xlabels)

    linestyles = ['-', '--', ':', '-.']

    data, leg1, leg2 = [], [], []
    for i, name in enumerate(csv_names):
        ls = linestyles[i%len(linestyles)]
        leg1.append(Line2D([0], [0], ls=ls, label=name))
        data.append(read_data(name))


    if not ylabels:
        ylabels = set()
        for df in data:
            for item in df.index.get_level_values(ychoice):
                ylabels.add(round(item, 6))
        ylabels = sorted(list(ylabels))


    colors = {ind: f"C{i%10}" for i, ind in enumerate(ylabels)}

    xset = set()
    for i, df in enumerate(data):

        indices = [round(x, 6) for x in df.index.get_level_values(ychoice)]
        ls = linestyles[i%len(linestyles)]

        for j, ylabel in enumerate(ylabels):

            marker = markers[j % len(markers)]
            color = colors[ylabel]

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
                res = optimize.curve_fit(fit.func, X, Y, guess, bounds=[min, max])
                step = abs(int((X[-1] - X[0])/100))
                pn = np.array(range(X[0], X[-1] + step, step))
                ft = fit.func(pn, *res[0])
                plt.plot(pn, ft, ls=ls, c=color)
                plt.plot(X, Y, lw=0, c=color, marker=marker, ms=ms, fillstyle="none")
                print(f"{ychoice} = {ylabel}", fit.show(*res[0]))
            else:
                plt.plot(X, Y, ls=ls, c=color, marker=marker, ms=ms, fillstyle="none")

            if i == 0:
                leg2.append(Line2D([0], [0], ls=ls, c=color, marker=marker, ms=ms, fillstyle="none", label=f"{ychoice}={ylabel}"))

            if plot_error and f"{feature}_v" in d:
                E = list(d.loc[:, f"{feature}_v"])
                ym = [y - e for y, e in zip(Y, E)]
                yp = [y + e for y, e in zip(Y, E)]
                plt.fill_between(X, ym, yp, alpha=0.1, facecolor=color, edgecolor=color, ls=ls, lw=2)


    xnames = sorted(list(xset)) if not xlabels else xlabels
    xticks = [x**dim for x in xnames]
    xnames = [round(x*xm, 3) for x in xnames]

    plt.xticks(xticks, xnames)
    L1 = plt.legend(handles=leg1, loc="lower right")
    plt.gca().add_artist(L1)
    L2 = plt.legend(handles=leg2, loc="upper left", ncol=3)
    plt.gca().add_artist(L2)

    plot_style(plt.gca(), "heuristic of {}".format(feature), xchoice, "{} count".format(feature))
    plt.show()



if __name__ == "__main__":

    import argparse
    from run_oopsc import add_kwargs

    parser = argparse.ArgumentParser(
        prog="threshold_compare",
        description="can compare thresholds and other paramters of different sims",
    )

    parser.add_argument("feature",
        action="store",
        type=str,
        help="feature to plot",
        metavar="feat",
    )

    parser.add_argument("xaxis",
        action="store",
        type=str,
        help="xaxis of comparison {l/p}",
        choices=["l", "p"],
        metavar="xaxis")

    key_arguments= [
        ["-n", "--csv_names", "store", "CSV databases to plot - verbose list str", dict(type=str, nargs='*', metavar="", required=True)],
        ["-p", "--probs", "store", "p items to plot - verbose list", dict(type=float, nargs='*', metavar="")],
        ["-l", "--latts", "store", "L items to plot - verbose list", dict(type=float, nargs='*', metavar="")],
        ["-e", "--plot_error", "store_true", "plot standard deviation - toggle", dict()],
        ["-a", "--average", "store_true", "average p - toggle", dict()],
        ["-f", "--fitname", "store", "fit class name", dict(type=str, default="", metavar="")],
        ["-d", "--dim", "store", "dimension", dict(type=int, default=1, metavar="")],
        ["-ms", "--ms", "store", "markersize", dict(type=int, default=5, metavar="")],
        ["-m", "--xm", "store", "x axis multiplier", dict(type=int, default=1, metavar="")],
        ["-o", "--output", "store", "output file name", dict(type=str, default="", metavar="")],
    ]
    add_kwargs(parser, key_arguments)
    args=vars(parser.parse_args())

    plot_compare(**args)
