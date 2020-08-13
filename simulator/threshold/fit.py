'''
2020 Mark Shui Hu

www.github.com/watermarkhu/OpenSurfaceSim
_____________________________________________

'''
import numpy as np
from scipy import optimize
from .sim import get_data


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


def fit_thresholds(data, modified_ansatz=False, latts=[], probs=[]):

    fitL, fitp, fitN, fitt = get_data(data, latts, probs)

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
