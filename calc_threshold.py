import numpy as np
import pandas as pd
from scipy import optimize


file_name = None
folder = "../../../OneDrive - Delft University of Technology/MEP - thesis Mark/Simulations/"

if file_name is None:
    file_name = input("Select data file: ")


data = pd.read_csv(folder + "data/" + file_name + ".csv", index_col=0)
thresholds = np.array(data)
numlat = len(data.index.values)
p = [float(k) for k in data.columns.values]
L = [float(k) for k in data.index.values]

# def make_fit(L):
#     fitfunc = lambda p, px: p[1] + p[2]*(px - p[0])*L**(1/p[5]) + p[3]*((px - p[0])*L**(1/p[5]))**2 + p[4]*L**(-1/p[6])
#     errfunc = lambda p, px, psucc: fitfunc(p, px) - psucc
#     return
#
# p0 = [0.1, 0, 0, 0, 0.165, 1.461, 0.71]
#
# for i, l in enumerate(L):
#     fit = make_fit(l)
#     p0, succes = optimize.leastsq(fit, p0[:], args=(p, thresholds[i]), maxfev=10000)
# p0



fits = []
for i in range(numlat):
    fits.append(np.polyfit(p, thresholds[i, :], 2))

thresholds = []
for i0, fit0 in enumerate(fits[:-1]):
    for fit1 in fits[i0 + 1:]:
        roots = np.roots(np.array(fit0) - np.array(fit1))
        thresholds += list(roots[(roots > 0.08) & (roots < 0.12)])

print("\nThe threshold is at " + str(np.mean(thresholds)*100) + "% with a std of " + str(np.std(thresholds)*100) + "%\n")
