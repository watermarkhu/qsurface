'''
2020 Mark Shui Hu, QuTech

www.github.com/watermarkhu/toric_code
_____________________________________________

'''
from matplotlib import pyplot as plt
from run_surface_code import multiprocess, decoder_config
from collections import defaultdict
from scipy import optimize
from pprint import pprint
import numpy as np
import pandas as pd
import git
import sys
import os


def plot_thresholds(
    fitL,                       # lattice size
    fitp,                       # p value
    fitN,                       # number of total simulations
    fitt,                       # number of successes
    plot_name="",               # Plot title
    data_select=None,           # in ["even", "odd"], selects even or odd lattices to plot
    modified_ansatz=False,      # uses the modifined ansatz for plotting
    plotn=1000,                 # number of points on x axis
    show_plot=True,             # show plotted figure
    ax0=None,                   # axis object of error fit plot
    ax1=None,                   # axis object of rescaled fit plot
    styles=[".", "-"]           # linestyles for data and fit
):
    '''
    Plot and fit thresholds for a given dataset. Data is inputted as four lists for L, P, N and t.
    '''
    if ax0 is None:
        f0, ax0 = plt.subplots()
    if ax1 is None:
        f1, ax1 = plt.subplots()

    if data_select in ["even", "odd"]:
        res = 0 if data_select == "even" else 1
        newval = [val for val in zip(fitL, fitp, fitN, fitt) if val[0] % 2 == res]
        fitL = [val[0] for val in newval]
        fitp = [val[1] for val in newval]
        fitN = [val[2] for val in newval]
        fitt = [val[3] for val in newval]

    LP = defaultdict(list)
    for L, P, N, T in zip(fitL, fitp, fitN, fitt):
        LP[L].append([P, N, T])

    '''
    Fitting function
    '''
    def fit_func(PL, pthres, A, B, C, D, nu, mu):
        p, L = PL
        x = (p - pthres) * L ** (1 / nu)
        if modified_ansatz:
            return A + B * x + C * x ** 2 + D * L ** (-1 / mu)
        else:
            return A + B * x + C * x ** 2

    '''
    Initial parameters for fitting function
    '''
    g_T, T_m, T_M = (min(fitp) + max(fitp))/2, min(fitp), max(fitp)
    g_A, A_m, A_M = 0, -np.inf, np.inf
    g_B, B_m, B_M = 0, -np.inf, np.inf
    g_C, C_m, C_M = 0, -np.inf, np.inf
    gnu, num, nuM = 1.46, 1.2, 1.6

    D_m, D_M = -2, 2
    mum, muM = 0, 3
    if data_select == "even":
        g_D, gmu = 1.65, 0.71
    elif data_select == "odd":
        g_D, gmu = -0.053, 2.1
    else:
        g_D, gmu = 0, 1

    par_guess = [g_T, g_A, g_B, g_C, g_D, gnu, gmu]
    bound = [(T_m, A_m, B_m, C_m, D_m, num, mum), (T_M, A_M, B_M, C_M, D_M, nuM, muM)]

    '''
    Fitting data
    '''
    par, pcov = optimize.curve_fit(
        fit_func,
        (fitp, fitL),
        [t / N for t, N in zip(fitt, fitN)],
        par_guess,
        bounds=bound,
        sigma=[max(fitN) / n for n in fitN],
    )
    perr = np.sqrt(np.diag(pcov))
    print("Least squared fitting on dataset results:")
    print("Threshold =", par[0], "+-", perr[0])
    print("A=", par[1], "B=", par[2], "C=", par[3])
    print("D=", par[4], "nu=", par[5], "mu=", par[6])

    '''
    Plot all results from file (not just current simulation)
    '''
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
    ax0.set_title("Threshold of " + plot_name)
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


if __name__ == "__main__":

    '''
    ############################################
                    options
    '''

    import unionfind_evengrow_integrated as decoder
    import graph_3D as go

    ltype = "toric"
    lattices = [44]
    P = [0.034]
    # P = list(np.round(np.linspace(0.096, 0.106, 3), 6))
    # P = list(np.round(np.linspace(0.024, 0.034, 2), 6))
    Num = 1
    P_store = 1000
    recursion_depth = 100000

    just_plot = 0
    print_data = 1
    save_result = 0
    data_select = None
    modified_ansatz = 0
    file_name = "toric_3D_uf_test"
    plot_name = file_name

    '''
    ############################################
    '''
    sys.setrecursionlimit(recursion_depth)

    r = git.Repo()
    hash = r.git.rev_parse(r.head, short=True)

    folder = "./"
    path = file_name if just_plot else hash + "_" + file_name
    file_path = folder + "./data/" + path + ".csv"
    fig_path = folder + "./figures/" + path + ".pdf"

    data = None
    int_P = [int(p*P_store) for p in P]

    # Simulate and save results to file
    if not just_plot:
        for lati in lattices:
            for pi, int_p in zip(P, int_P):

                print("Calculating for L = ", str(lati), "and p =", str(pi))

                output = multiprocess(Num, decoder_config(), decoder, go, pX=pi, pmX=pi, ltype=ltype, size=lati)

                pprint(dict(output), "\n")
                columns = list(output.keys())

                if data is None:
                    if os.path.exists(file_path):
                        data = pd.read_csv(file_path, header=0)
                        data = data.set_index(["L", "p"])
                    else:
                        index = pd.MultiIndex.from_product([lattices, int_P], names=["L", "p"])
                        data = pd.DataFrame(
                            np.zeros((len(lattices) * len(P), len(columns))), index=index, columns=columns
                        )

                if data.index.isin([(lati, int_p)]).any():
                    for key, value in output.items():
                        data.loc[(lati, int_p), key] += value
                else:
                    for key, value in output.items():
                        data.loc[(lati, int_p), key] = value

                data = data.sort_index()
                if save_result:
                    data.to_csv(file_path)

    print(data.to_string()) if print_data else None

    '''Select data to plot'''
    fitL = data.index.get_level_values("L")
    fitp = data.index.get_level_values("p")
    fitN = data.loc[:, "N"].values
    fitt = data.loc[:, "succes"].values

    fitdata = [[] for i in range(4)]
    for L, p, N, t in zip(fitL, fitp, fitN, fitt):
        if N != 0:
            fitdata[0].append(L)
            fitdata[1].append(p/P_store)
            fitdata[2].append(N)
            fitdata[3].append(t)

    f0, ax0 = plt.subplots()
    f1, ax1 = plt.subplots()
    plot_thresholds(*fitdata, plot_name=file_name, ax0=ax0, ax1=ax1, modified_ansatz=modified_ansatz)
    plt.show()

    if save_result:
        data.to_csv(file_path)
        f0.savefig(fig_path, transparent=True, format="pdf", bbox_inches="tight")
