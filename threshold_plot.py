from collections import defaultdict
import matplotlib.pyplot as plt
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


def plot_thresholds(
    data,
    plot_title="",               # Plot title
    fig_path="",
    modified_ansatz=False,
    data_select=False,
    show_plot=True,             # show plotted figure
    save_result=True,
    ax0=None,                   # axis object of error fit plot
    ax1=None,                   # axis object of rescaled fit plot
    par=None,
    lattices=None,
):

    styles=[".", "-"]           # linestyles for data and fit
    plotn=1000                  # number of points on x axis

    '''
    apply fit and get parameter
    '''
    if par is None:
        par = fit_data(data, modified_ansatz, data_select)

    fit_func = get_fit_func(modified_ansatz)

    '''
    Plot and fit thresholds for a given dataset. Data is inputted as four lists for L, P, N and t.
    '''

    fitL, fitp, fitN, fitt = get_data(data, data_select)

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

    for i, lati in enumerate(lattices):
        fp, fN, fs = map(list, zip(*sorted(LP[lati], key=lambda k: k[0])))
        ft = [si / ni for si, ni in zip(fs, fN)]
        ax0.plot(
            [q * 100 for q in fp], ft, styles[0], color=colors[lati], ms=5
        )
        X = np.linspace(min(fp), max(fp), plotn)
        ax0.plot(
            [x * 100 for x in X],
            [fit_func((x, lati), *par) for x in X],
            "-",
            label="L = {}".format(lati),
            color=colors[lati],
            lw=1.5,
            alpha=0.6,
            ls=styles[1],
        )

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
    ax0.set_ylim(0.5, 1)
    ax0.legend()

    ''' Plot using the rescaled error rate'''

    for L, p, N, t in zip(fitL, fitp, fitN, fitt):
        if L in lattices:
            if modified_ansatz:
                plt.plot(
                    (p - par[0]) * L ** (1 / par[5]),
                    t / N - par[4] * L ** (-1 / par[6]),
                    ".",
                    color=colors[L],
                )
            else:
                plt.plot(
                    (p - par[0]) * L ** (1 / par[5]),
                    t / N,
                    ".",
                    color=colors[L],
                )
    x = np.linspace(*plt.xlim(), plotn)
    ax1.plot(x, par[1] + par[2] * x + par[3] * x ** 2, "--", color="C0", alpha=0.5)

    plot_style(ax1, "Modified curve " + plot_title, "Rescaled error rate", "Modified succces probability")

    if show_plot:
        plt.show()

    if save_result:
        f0.savefig(fig_path, transparent=True, format="pdf", bbox_inches="tight")


if __name__ == "__main__":

    import argparse
    from oopsc import add_args

    parser = argparse.ArgumentParser(
        prog="threshold_fit",
        description="fit a threshold computation",
        usage='%(prog)s [-h/--help] file_name'
    )

    parser.add_argument("file_name",
        action="store",
        type=str,
        help="file name of csv data (without extension)",
        metavar="file_name",
    )

    key_arguments = [
        ["-ds", "--data_select", "store", "selective plot data - {even/odd}", dict(type=str, choices=["even", "odd"], metavar="")],
        ["-l", "--lattices", "store", "lattice sizes - verbose list int", dict(type=int, nargs='*', metavar="")],
        ["-ma", "--modified_ansatz", "store_true", "use modified ansatz - toggle", dict()],
        ["-s", "--save_result", "store_true", "save results - toggle", dict()],
        ["-pt", "--plot_title", "store", "plot filename - toggle", dict(default="")],
        ["-f", "--folder", "store", "base folder path - toggle", dict(default="./")],
    ]

    add_args(parser, key_arguments)
    args=vars(parser.parse_args())

    folder = args.pop("folder")
    name = args.pop("file_name")
    data = read_data(folder + "data/" + name + ".csv", args.pop("lattices"))
    fig_path = folder + "figures/" + name + ".pdf"
    plot_thresholds(data, fig_path=fig_path, **args)
