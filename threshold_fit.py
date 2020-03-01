from scipy import optimize
import numpy as np
import pandas as pd


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


def fit_data(data, modified_ansatz=False, data_select=None):

    fitL, fitp, fitN, fitt = get_data(data, data_select)

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
        ["-f", "--folder", "store", "base folder path - toggle", dict(default="./")],
        ["-ma", "--modified_ansatz", "store_true", "use modified ansatz - toggle", dict()],
        ["-ds", "--data_select", "store", "selective plot data - {even/odd}", dict(type=str, choices=["even", "odd"], metavar="")]
    ]

    add_args(parser, key_arguments)
    args=vars(parser.parse_args())

    data = read_data(args.pop("folder") + "data/" + args.pop("file_name") + ".csv")
    fit_data(data, **args)
