from . import oopsc
from pprint import pprint
import multiprocessing as mp
import numpy as np
import pandas as pd
from scipy import optimize
import git, sys, os
from collections import defaultdict
import matplotlib.pyplot as plt


def read_data(file_path):
    try:
        data = pd.read_csv(file_path, header=0)
        return data.set_index(["L", "p"])

    except FileNotFoundError:
        print("File not found")
        exit()


def get_data(data, data_select=None, P_store=1000):

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

    if data_select in ["even", "odd"]:
        res = 0 if data_select == "even" else 1
        fitdata = list(map(list, zip(*[val for val in zip(*fitdata) if val[0] % 2 == res])))

    return fitdata[0], fitdata[1], fitdata[2], fitdata[3]


def get_fit_func(modified_ansatz=False):
    if modified_ansatz:
        return fit_func_m
    else:
        return fit_func

def fit_func(PL, pthres, A, B, C, D, nu, mu):
    p, L = PL
    x = (p - pthres) * L ** (1 / nu)
    return A + B * x + C * x ** 2


def fit_func_m(PL, pthres, A, B, C, D, nu, mu):
    p, L = PL
    x = (p - pthres) * L ** (1 / nu)
    return A + B * x + C * x ** 2 + D * L ** (-1 / mu)


def fit_thresholds(data, modified_ansatz=False, data_select=None):

    fitL, fitp, fitN, fitt = get_data(data, data_select, 1)

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
    ffit = get_fit_func(modified_ansatz)

    par, pcov = optimize.curve_fit(
        ffit,
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

    return par


def plot_thresholds(
    data,
    plot_title="",               # Plot title
    fig_path="",
    modified_ansatz=False,
    data_select=False,
    show_plot=True,             # show plotted figure
    save_result=False,
    f0=None,                   # axis object of error fit plot
    f1=None,                   # axis object of rescaled fit plot
    par=None,
    styles=[".", "-"]           # linestyles for data and fit

):

    plotn=1000                  # number of points on x axis

    '''
    apply fit and get parameter
    '''
    if par is None:
        par = fit_thresholds(data, modified_ansatz, data_select)

    fit_func = get_fit_func(modified_ansatz)

    '''
    Plot and fit thresholds for a given dataset. Data is inputted as four lists for L, P, N and t.
    '''

    fitL, fitp, fitN, fitt = get_data(data, data_select, 1)

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

    print(par[0])

    # ax0.axvline(par[0] * 100, ls="dotted", color="k", alpha=0.5)
    ax0.annotate(
        "$p_t$ = {}%, DS = {:.2f}".format(str(round(100 * par[0], 2)), DS),
        (par[0] * 100, DS),
        xytext=(10, 10),
        textcoords="offset points",
        fontsize=8,
    )
    ax0.set_title(plot_title)
    ax0.set_xlabel("probability of Pauli X error (%)")
    ax0.set_ylabel("decoding success rate")
    ax0.legend(ncol=2, loc="lower left")

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
        f0.tight_layout()
        plt.show()

    if save_result:
        f0.savefig(fig_path, transparent=True, format="pdf", bbox_inches="tight")

    return f0, f1


def sim_thresholds(
        decoder,
        lattice_type="toric",
        lattices = [],
        perror = [],
        iters = 0,
        measurement_error=False,
        multithreading=False,
        threads=None,
        modified_ansatz=False,
        save_result=True,
        file_name="thres",
        show_plot=False,
        plot_title=None,
        folder = "./",
        subfolder=False,
        P_store=1000,
        debug=False,
        progressbar=False,
        **kwargs
        ):
    '''
    ############################################
    '''

    run_oopsc = oopsc.multiprocess if multithreading else oopsc.multiple

    if measurement_error:
        from .graph import graph_3D as go
    else:
        from .graph import graph_2D as go

    sys.setrecursionlimit(100000)
    # r = git.Repo(os.path.dirname(__file__))
    # full_name = r.git.rev_parse(r.head, short=True) +

    get_name = lambda s: s[s.rfind(".")+1:]
    g_type = get_name(go.__name__)
    d_type = get_name(decoder.__name__)
    full_name = f"{lattice_type}_{g_type}_{d_type}_{file_name}"
    if not plot_title:
        plot_title = full_name

    if not os.path.exists(folder):
        os.makedirs(folder)

    if subfolder:
        os.makedirs(folder + "/data/", exist_ok=True)
        os.makedirs(folder + "/figures/", exist_ok=True)
        file_path = folder + "/data/" + full_name + ".csv"
        fig_path = folder + "/figures/" + full_name + ".pdf"
    else:
        file_path = folder + "/" + full_name + ".csv"
        fig_path = folder + "/" + full_name + ".pdf"

    data = None
    int_P = [int(p*P_store) for p in perror]
    config = oopsc.default_config(**kwargs)

    # Simulate and save results to file
    for lati in lattices:

        if multithreading:
            if threads is None:
                threads = mp.cpu_count()
            graph = [oopsc.lattice_type(lattice_type, config, decoder, go, lati) for _ in range(threads)]
        else:
            graph = oopsc.lattice_type(lattice_type, config, decoder, go, lati)

        for pi, int_p in zip(perror, int_P):

            print("Calculating for L = ", str(lati), "and p =", str(pi))

            oopsc_args = dict(
                paulix=pi,
                lattice_type=lattice_type,
                debug=debug,
                processes=threads,
                progressbar=progressbar
            )
            if measurement_error:
                oopsc_args.update(measurex=pi)
            output = run_oopsc(lati, config, iters, graph=graph, **oopsc_args)

            pprint(dict(output))
            print("")

            if data is None:
                if os.path.exists(file_path):
                    data = pd.read_csv(file_path, header=0)
                    data = data.set_index(["L", "p"])
                else:
                    columns = list(output.keys())
                    index = pd.MultiIndex.from_product([lattices, int_P], names=["L", "p"])
                    data = pd.DataFrame(
                        np.zeros((len(lattices) * len(perror), len(columns))), index=index, columns=columns
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

    print(data.to_string())

    par = fit_thresholds(data, modified_ansatz)

    if show_plot:
        plot_thresholds(data, file_name, fig_path, modified_ansatz, save_result=save_result, par=par)

    if save_result:
        data.to_csv(file_path)
