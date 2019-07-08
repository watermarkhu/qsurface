import numpy as np
from scipy.optimize import fsolve

p = list(np.linspace(0.09, 0.11, 11))
lat = [12, 16, 20]
pre = "Peeling_toric_only_pX_bucket_ncount_Thres_L"


fits = []
for size in lat:
    Name = pre + str(size) + "_N30000.txt"
    file = open(Name, 'r')
    eff = []
    for line in file.readlines():
        eff.append(float(line))
    fits.append(np.polyfit(p, eff, 2))

thresholds = []
for i0, fit0 in enumerate(fits[:-1]):
    for fit1 in fits[i0 + 1:]:
        roots = np.roots(np.array(fit0) - np.array(fit1))
        thresholds += list(roots[(roots > 0.08) & (roots < 0.12)])

print("The threshold is at " + str(np.mean(thresholds)*100) + "% with a std of " + str(np.std(thresholds)*100) + "%")
