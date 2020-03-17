from scipy import optimize
import numpy as np
import pandas as pd


def read_data(file_path):
    try:
        data = pd.read_csv(file_path, header=0)
        data = data.set_index(["L", "p"])
        return data

    except FileNotFoundError:
        print("File not found")
        quit()


def get_data(data, latts, probs, P_store=1):

    if not latts: latts = []
    if not probs: probs = []

    fitL = data.index.get_level_values("L")
    fitp = data.index.get_level_values("p")
    fitN = data.loc[:, "N"].values
    fitt = data.loc[:, "succes"].values

    fitdata = [[] for i in range(4)]
    for L, P, N, t in zip(fitL, fitp, fitN, fitt):
        p = round(float(P)/P_store, 6)
        if all([N != 0, not latts or L in latts, not probs or p in probs]):
            fitdata[0].append(L)
            fitdata[1].append(p)
            fitdata[2].append(N)
            fitdata[3].append(t)

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


def fit_data(data, modified_ansatz=False, latts=[], probs=[], P_store=1):

    fitL, fitp, fitN, fitt = get_data(data, latts, probs, P_store)

    '''
    Initial parameters for fitting function
    '''
    g_T, T_m, T_M = (min(fitp) + max(fitp))/2, min(fitp), max(fitp)
    g_A, A_m, A_M = 0, -np.inf, np.inf
    g_B, B_m, B_M = 0, -np.inf, np.inf
    g_C, C_m, C_M = 0, -np.inf, np.inf
    gnu, num, nuM = 0.974, 0.8, 1.2

    D_m, D_M = -2, 2
    mum, muM = 0, 3

    g_D, gmu = 1.65, 0.71
    # odd:
    # g_D, gmu = -0.053, 2.1

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

    return (fitL, fitp, fitN, fitt), par


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
    ]

    add_kwargs(parser, key_arguments)
    args=vars(parser.parse_args())

    data = read_data(args.pop("file_name"))
    fit_data(data, **args)
