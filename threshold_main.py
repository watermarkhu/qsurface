from matplotlib import pyplot as plt
from run_toric_2D_uf import multiprocess, multiple
from collections import defaultdict
from scipy import optimize
import numpy as np
import pandas as pd
import git
import os


def plot_thresholds(
    fitL,  # lattice size
    fitp,  # p value
    fitN,  # number of total simulations
    fitt,  # number of successes
    plot_name="",
    data_select=None,
    modified_ansatz=False,
    plotn=1000,
    show_plot=True,
    ax0=None,
    ax1=None,
    styles=[".", "-"]
):

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

    # Fitting using scripy optimize curve_fit

    def fit_func(PL, pthres, A, B, C, D, nu, mu):
        p, L = PL
        x = (p - pthres) * L ** (1 / nu)
        if modified_ansatz:
            return A + B * x + C * x ** 2 + D * L ** (-1 / mu)
        else:
            return A + B * x + C * x ** 2

    g_T, T_m, T_M = 0.1, min(fitp), max(fitp)
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

    # Plot all results from file (not just current simulation)
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
            label=lati,
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

    folder = "../thresholds/"

    just_plot = 0
    print_data = 1
    save_result = 1
    data_select = None
    modified_ansatz = 0
    file_name = "uf_toric_pX_bucket_MOPgrowth_Npeel"
    plot_name = file_name

    lattices = [12, 16, 20, 24, 28, 32]
    p = list(np.round(np.linspace(0.09, 0.11, 11), 21))
    Num = 50000

    r = git.Repo()
    hash = r.git.rev_parse(r.head, short=True)

    settings = {"ro": 0, "rt": 0, "vc": 0}

    file_path = (
        folder + "data/" + file_name + ".csv"
        if just_plot
        else folder + "data/" + hash + "_" + file_name + ".csv"
    )
    if os.path.exists(file_path):
        data = pd.read_csv(file_path, header=0)
        data = data.set_index(["L", "p"])
    else:
        index = pd.MultiIndex.from_product([lattices, p], names=["L", "p"])
        data = pd.DataFrame(
            np.zeros((len(lattices) * len(p), 2)), index=index, columns=["N", "succes"]
        )

    indices = data.index.values
    cols = ["N", "succes"]

    # Simulate and save results to file
    if not just_plot:
        for i, lati in enumerate(lattices):
            for pi in p:

                print("Calculating for L = ", str(lati), "and p =", str(pi))
                N_succes = multiprocess(
                    lati, Num, 0, pi, 0, processes=4, settings=settings
                )
                # N_succes = multiple(lati, Num, 0, pi, 0)

                if any([(lati, pi) == a for a in indices]):
                    data.loc[(lati, round(pi, 6)), "N"] += Num
                    data.loc[(lati, round(pi, 6)), "succes"] += N_succes
                else:
                    data.loc[(lati, round(pi, 6)), cols] = pd.Series(
                        [Num, N_succes]
                    ).values
                    data = data.sort_index()

                if save_result:
                    data.to_csv(file_path)

    print(data.to_string()) if print_data else None

    # Select data

    fitL = data.index.get_level_values("L")
    fitp = data.index.get_level_values("p")
    fitN = data.loc[:, "N"].values
    fitt = data.loc[:, "succes"].values

    f0, ax0 = plt.figure()
    f1, ax1 = plt.figure()
    plot_thresholds(fitL, fitp, fitN, fitt, plot_name=file_name, ax0=ax0, ax1=ax1)

    if save_result:
        data.to_csv(file_path)
        fname = folder + "./figures/" + hash + "_" + file_name + ".pdf"
        f0.savefig(fname, transparent=True, format="pdf", bbox_inches="tight")
