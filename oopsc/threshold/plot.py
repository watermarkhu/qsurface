'''
2020 Mark Shui Hu, QuTech

www.github.com/watermarkhu/oop_surface_code
_____________________________________________

'''
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from collections import defaultdict
from scipy import optimize
import numpy as np
import math
from .fit import fit_thresholds, get_fit_func
from .sim import get_data, read_data


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


def plot_thresholds(
    file_name,
    plot_title="",               # Plot title
    output="",
    modified_ansatz=False,
    latts=[],
    probs=[],
    show_plot=True,             # show plotted figure
    f0=None,                   # axis object of error fit plot
    f1=None,                   # axis object of rescaled fit plot
    par=None,
    lattices=None,
    ms=5,
    ymax=1,
    ymin=0.5,
    styles=[".", "-"],           # linestyles for data and fit
    plotn=1000                  # number of points on x axis
):

    data = read_data(file_name)
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

    if f0 is None:
        f0, ax0 = plt.subplots()
    else:
        ax0 = f0.axes[0]
    if f1 is None:
        f1, ax1 = plt.subplots()
    else:
        ax1 = f1.axes[0]

    LP = defaultdict(list)
    for L, P, N, T in zip(fitL, fitp, fitN, fitt):
        LP[L].append([P, N, T])

    if lattices is None:
        lattices = sorted(set(fitL))

    colors = {lati:f"C{i%10}" for i, lati in enumerate(lattices)}
    markerlist = get_markers()
    markers = {lati: markerlist[i%len(markerlist)] for i, lati in enumerate(lattices)}
    legend = []

    for i, lati in enumerate(lattices):
        fp, fN, fs = map(list, zip(*sorted(LP[lati], key=lambda k: k[0])))
        ft = [si / ni for si, ni in zip(fs, fN)]
        ax0.plot(
            [q * 100 for q in fp], ft, styles[0],
            color=colors[lati],
            marker=markers[lati],
            ms=ms,
            fillstyle="none",
        )
        X = np.linspace(min(fp), max(fp), plotn)
        ax0.plot(
            [x * 100 for x in X],
            [fit_func((x, lati), *par) for x in X],
            "-",
            color=colors[lati],
            lw=1.5,
            alpha=0.6,
            ls=styles[1],
        )

        legend.append(Line2D(
            [0],
            [0],
            ls=styles[1],
            label="L = {}".format(lati),
            color=colors[lati],
            marker=markers[lati],
            ms=ms,
            fillstyle="none"
        ))


    DS = fit_func((par[0], 20), *par)

    # ax0.axvline(par[0] * 100, ls="dotted", color="k", alpha=0.5)
    ax0.annotate(
        "$p_t$ = {}%, DS = {:.2f}".format(str(round(100 * par[0], 2)), DS),
        (par[0] * 100, DS),
        xytext=(10, 10),
        textcoords="offset points",
        fontsize=8,
    )

    plot_style(ax0, plot_title, "probability of Pauli X error (%)", "decoding success rate")
    ax0.set_ylim(ymin, ymax)
    ax0.legend(handles=legend, loc="lower left", ncol=2)

    ''' Plot using the rescaled error rate'''

    for L, p, N, t in zip(fitL, fitp, fitN, fitt):
        if L in lattices:
            if modified_ansatz:
                plt.plot(
                    (p - par[0]) * L ** (1 / par[5]),
                    t / N - par[4] * L ** (-1 / par[6]),
                    ".",
                    color=colors[L],
                    marker=markers[L],
                    ms=ms,
                    fillstyle="none",
                )
            else:
                plt.plot(
                    (p - par[0]) * L ** (1 / par[5]),
                    t / N,
                    ".",
                    color=colors[L],
                    marker=markers[L],
                    ms=ms,
                    fillstyle="none",
                )
    x = np.linspace(*plt.xlim(), plotn)
    ax1.plot(x, par[1] + par[2] * x + par[3] * x ** 2, "--", color="C0", alpha=0.5)
    ax1.legend(handles=legend, loc="lower left", ncol=2)

    plot_style(ax1, "Modified curve " + plot_title, "Rescaled error rate", "Modified succces probability")

    if show_plot:
        plt.show()

    if output:
        if output [-4:] != ".pdf": output += ".pdf"
        f0.savefig(output, transparent=True, format="pdf", bbox_inches="tight")

    return f0, f1

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

    plot_style(plt.gca(), "Comparison of {}".format(feature), xchoice, "{} count".format(feature))
    plt.show()
