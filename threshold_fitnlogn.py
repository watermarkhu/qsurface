from scipy import optimize
from threshold_fit import read_data
import matplotlib.pyplot as plt
import numpy as np
import math

path = "simulations/cartesius/data/eg_planar_3d.csv"
data = read_data(path)

P = sorted(list(set([round(x, 6) for x in data.index.get_level_values("p")])))

for p in P:

    row = data.loc[np.round(data.index.get_level_values("p"), 6) == p, "gbo_m"]
    N = [x**3 for x in row.index.get_level_values("L")]
    T = list(row)

    # del N[-1]
    # del T[-1]
    # del N[-3]
    # del T[-3]

    def fit_func(N, A, B, C,):
        return A*N*(np.log(N)/math.log(B))**C


    guess = [0.01, 10, 1]
    min = (0, 1, 1)
    max = (1, 1000000, 100)

    res = optimize.curve_fit(fit_func, N, T, guess, bounds=[min, max])
    pn = np.array(range(N[0], N[-1] +1))
    ft = fit_func(pn, *res[0])

    print(p, res[0][1], res[0][2])

    plt.plot(pn, ft, label=str(p))
    plt.plot(N, T, "x")
plt.legend()
plt.show()
