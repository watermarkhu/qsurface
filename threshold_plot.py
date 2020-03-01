from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np
from threshold_fit import get_data, get_fit_func, fit_data, read_data


'''Select data to plot'''

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

    plot_i = {}
    for i, l in enumerate(set(fitL)):
        plot_i[l] = i

    for lati in sorted(set(fitL)):
        fp, fN, fs = map(list, zip(*sorted(LP[lati], key=lambda k: k[0])))
        ft = [si / ni for si, ni in zip(fs, fN)]
        ax0.plot(
            [q * 100 for q in fp], ft, styles[0], color="C" + str(plot_i[lati] % 10), ms=5
        )
        X = np.linspace(min(fp), max(fp), plotn)
        ax0.plot(
            [x * 100 for x in X],
            [fit_func((x, lati), *par) for x in X],
            "-",
            label="L = {}".format(lati),
            color="C" + str(plot_i[lati] % 10),
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
    ax0.set_title("Threshold of " + plot_title)
    ax0.set_xlabel("probability of Pauli X error (%)")
    ax0.set_ylabel("decoding success rate")
    ax0.legend()

    ''' Plot using the rescaled error rate'''

    for L, p, N, t in zip(fitL, fitp, fitN, fitt):
        if modified_ansatz:
            plt.plot(
                (p - par[0]) * L ** (1 / par[5]),
                t / N - par[4] * L ** (-1 / par[6]),
                ".",
                color="C" + str(plot_i[L] % 10),
            )
        else:
            plt.plot(
                (p - par[0]) * L ** (1 / par[5]),
                t / N,
                ".",
                color="C" + str(plot_i[L] % 10),
            )
    x = np.linspace(*plt.xlim(), plotn)
    ax1.plot(x, par[1] + par[2] * x + par[3] * x ** 2, "--", color="C0", alpha=0.5)
    ax1.set_xlabel("Rescaled error rate")
    ax1.set_ylabel("Modified succces probability")


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
        ["-ma", "--modified_ansatz", "store_true", "use modified ansatz - toggle", dict()],
        ["-s", "--save_result", "store_true", "save results - toggle", dict()],
        ["-pt", "--plot_title", "store", "plot filename - toggle", dict(default="")],
        ["-f", "--folder", "store", "base folder path - toggle", dict(default="./")],
    ]

    add_args(parser, key_arguments)
    args=vars(parser.parse_args())

    folder = args.pop("folder")
    name = args.pop("file_name")
    data = read_data(folder + "data/" + name + ".csv")
    fig_path = folder + "figures/" + name + ".pdf"
    plot_thresholds(data, **args)
