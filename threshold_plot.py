from collections import defaultdict
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
from threshold_fit import get_data, get_fit_func, fit_data, read_data


'''Select data to plot'''

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
    data,
    plot_title="",               # Plot title
    output="",
    modified_ansatz=False,
    latts=[],
    probs=[],
    show_plot=True,             # show plotted figure
    ax0=None,                   # axis object of error fit plot
    ax1=None,                   # axis object of rescaled fit plot
    par=None,
    lattices=None,
    ms=5,
    ymax=1,
    ymin=0.5,
):

    styles=[".", "-"]           # linestyles for data and fit
    plotn=1000                  # number of points on x axis

    '''
    apply fit and get parameter
    '''
    if par is None:
        (fitL, fitp, fitN, fitt), par = fit_data(data, modified_ansatz, latts, probs)
    else:
        fitL, fitp, fitN, fitt = get_data(data, latts, probs)


    fit_func = get_fit_func(modified_ansatz)

    '''
    Plot and fit thresholds for a given dataset. Data is inputted as four lists for L, P, N and t.
    '''

    if ax0 is None:
        f0, ax0 = plt.subplots()
    if ax1 is None:
        f1, ax1 = plt.subplots()

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

    ax0.axvline(par[0] * 100, ls="dotted", color="k", alpha=0.5)
    ax0.annotate(
        "$p_t$ = {}%, DS = {:.2f}".format(str(round(100 * par[0], 2)), DS),
        (par[0] * 100, DS),
        xytext=(10, 10),
        textcoords="offset points",
        fontsize=8,
    )

    plot_style(ax0, "Threshold of " + plot_title, "probability of Pauli X error (%)", "decoding success rate")
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


if __name__ == "__main__":

    import argparse
    from oopsc import add_kwargs

    parser = argparse.ArgumentParser(
        prog="threshold_fit",
        description="fit a threshold computation",
        usage='%(prog)s [-h/--help] file_name'
    )

    parser.add_argument("file_name",
        action="store",
        type=str,
        help="file name of csv data (with extension)",
        metavar="file_name",
    )

    key_arguments = [
        ["-p", "--probs", "store", "p items to plot - verbose list", dict(type=float, nargs='*', metavar="")],
        ["-l", "--latts", "store", "L items to plot - verbose list", dict(type=float, nargs='*', metavar="")],
        ["-ma", "--modified_ansatz", "store_true", "use modified ansatz - toggle", dict()],
        ["-o", "--output", "store", "output file name", dict(type=str, default="", metavar="")],
        ["-pt", "--plot_title", "store", "plot filename", dict(type=str, default="", metavar="")],
        ["-ymin", "--ymin", "store", "limit yaxis min", dict(type=float, default=0.5, metavar="")],
        ["-ymax", "--ymax", "store", "limit yaxis max", dict(type=float, default=1, metavar="")],

    ]

    add_kwargs(parser, key_arguments)
    args=vars(parser.parse_args())

    data = read_data(args.pop("file_name"))
    plot_thresholds(data, **args)
