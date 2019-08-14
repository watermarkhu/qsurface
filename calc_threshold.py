import numpy as np
import pandas as pd



file_name = None
folder = "../../../OneDrive - Delft University of Technology/MEP - thesis Mark/Simulations/"

if file_name is None:
    file_name = input("Select data file: ")


data = pd.read_csv(folder + "data/" + file_name + ".csv", index_col=0)
thresholds = np.array(data)
numlat = len(data.index.values)
p = [float(k) for k in data.columns.values]


fits = []
for i in range(numlat):
    fits.append(np.polyfit(p, thresholds[i, :], 2))

thresholds = []
for i0, fit0 in enumerate(fits[:-1]):
    for fit1 in fits[i0 + 1:]:
        roots = np.roots(np.array(fit0) - np.array(fit1))
        thresholds += list(roots[(roots > 0.08) & (roots < 0.12)])

print("\nThe threshold is at " + str(np.mean(thresholds)*100) + "% with a std of " + str(np.std(thresholds)*100) + "%\n")
