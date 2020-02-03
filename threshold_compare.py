import pandas as pd
import matplotlib.pyplot as plt

file_name1 = "64d9f77_threshold_fixed_uf_egiv2_dgv"
file_name2 = "5542ff6_threshold_fixed_uf_evengrow_v2"
folder = "./"
file_path1 = folder + "./data/" + file_name1 + ".csv"
file_path2 = folder + "./data/" + file_name2 + ".csv"


data1 = pd.read_csv(file_path1, header=0)
data1 = data1.set_index(["L", "p"])

data2 = pd.read_csv(file_path2, header=0)
data2 = data2.set_index(["L", "p"])

i1 = list(zip(*data1.index.values.tolist()))
i2 = list(zip(*data2.index.values.tolist()))

L = sorted(list(set(i1[0]) & set(i2[0])))
P = sorted(list(set(i1[1]) & set(i2[1])))

plt.figure()
for lati in L:

    l = []
    for pi in P:
        num1 = data1.loc[(lati, round(pi, 6)), "N"]
        suc1 = data1.loc[(lati, round(pi, 6)), "succes"]

        num2 = data2.loc[(lati, round(pi, 6)), "N"]
        suc2 = data2.loc[(lati, round(pi, 6)), "succes"]

        l.append((suc1/num1 - suc2/num2)*100)
    plt.plot(P, l, label=str(lati))
plt.xlabel("pX")
plt.ylabel("Decoder improvement (%)")
plt.title("mwpm decoder improvement over uf-dgvertices decoder")
plt.legend()
plt.show()
