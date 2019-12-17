import pandas as pd
import matplotlib.pyplot as plt

file_name2 = "da3c8b0_threshold_fixed_list_dgvertices_smallp"
file_name1 = "da3c8b0_threshold_fixed_mwpm_blossom5_smallp"
folder = "./"
file_path1 = folder + "./data/" + file_name1 + ".csv"
file_path2 = folder + "./data/" + file_name2 + ".csv"


data1 = pd.read_csv(file_path1, header=0)
data1 = data1.set_index(["L", "p"])

data2 = pd.read_csv(file_path2, header=0)
data2 = data2.set_index(["L", "p"])


lattices = [8,9,10,11]
P = [(90 + 2*i)/1000 for i in range(11)]


plt.figure()
for lati in lattices:

    l = []
    for pi in P:
        num1 = data1.loc[(lati, round(pi, 6)), "N"]
        suc1 = data1.loc[(lati, round(pi, 6)), "succes"]

        num2 = data2.loc[(lati, round(pi, 6)), "N"]
        suc2 = data2.loc[(lati, round(pi, 6)), "succes"]

        l.append((suc1/num1 - suc2/num2)*100)
    plt.plot(l, label=str(lati))
plt.xlabel("pX")
plt.ylabel("Decoder improvement (%)")
plt.title("mwpm decoder improvement over uf-dgvertices decoder")
plt.legend()
plt.show()
