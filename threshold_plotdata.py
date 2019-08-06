from matplotlib import pyplot as plt
import numpy as np
import pandas as pd

file_name = "190801_peeling_toric_pX_bucket_ao=rand_rt=on_N60000"
plot_name = "Peeling decoder (toric) vs. Pauli X error rate (bucket, ao=rand, rt=on)"


data = pd.read_csv("./data/" + file_name + ".csv", index_col=0)
thresholds = np.array(data)
lattices = [int(k) for k in data.index.values]
p = [float(k) for k in data.columns.values]

plotn = 500
X = np.linspace(p[0], p[-1], plotn)
f0 = plt.figure()


for i, (lat, thres) in enumerate(zip(lattices, thresholds)):
    fit = np.polyfit(p, thres, 2)
    polyfit = np.poly1d(fit)
    plt.plot([pi*100 for pi in p], thres, 'x', color='C'+str(i))
    plt.plot([x*100 for x in X], polyfit(X), '-', label=lat, color='C'+str(i))

plt.title(plot_name)
plt.legend()
plt.xlabel("probability Pauli X error (%)")
plt.ylabel("Decoding success rate (%)")
plt.show()
fname = "./figures/" + file_name + ".pdf"
# f0.savefig(fname, transparent=True, format="pdf", bbox_inches="tight")
