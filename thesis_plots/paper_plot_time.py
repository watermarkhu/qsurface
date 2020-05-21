
import matplotlib.pyplot as plt
from threshold_fit import read_data
from matplotlib.lines import Line2D
from matplotlib.patches import Patch


def plot_style(ax, title=None, xlabel=None, ylabel=None, **kwargs):
    ax.grid(linestyle=':', linewidth=.5)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    for key, arg in kwargs.items():
        func = getattr(ax, f"set_{key}")
        func(arg)
    # ax.patch.set_facecolor('0.95')
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.spines["left"].set_visible(False)

def get_markers():
    return ["o", "*", "v", ">", "<", "^", "h", "X", "<", "P", "*", ">", "H", "d", 4, 5, 6, 7, 8, 9, 10, 11]



def plot_compare(ax, color, csv_names, xaxis, probs, latts, feature, dim, **kwargs):


    markers = get_markers()

    xchoice = dict(p="p", P="p", l="L", L="L")
    ychoice = dict(p="L", P="L", l="p", L="p")
    xchoice, ychoice = xchoice[xaxis], ychoice[xaxis]
    xlabels, ylabels = (probs, latts) if xaxis == "p" else (latts, probs)
    if xlabels: xlabels = sorted(xlabels)

    linestyles = ['-', '--', ':', '-.']

    data, leg1, leg2 = [], [], []
    for i, name in enumerate(csv_names):
        ls = linestyles[i%len(linestyles)]
        leg1.append(Line2D([0], [0], ls=ls, label=name))
        data.append(read_data(name))


    if not ylabels:
        ylabels = set()
        for df in data:
            for item in df.index.get_level_values(ychoice):
                ylabels.add(round(item, 6))
        ylabels = sorted(list(ylabels))

    xset = set()
    for i, df in enumerate(data):

        indices = [round(x, 6) for x in df.index.get_level_values(ychoice)]
        ls = linestyles[i%len(linestyles)]


        Y = []

        for j, ylabel in enumerate([ylabels[0], ylabels[-1]]):

            marker = markers[j % len(markers)]

            d = df.loc[[x == ylabel for x in indices]]
            index = [round(v, 6) for v in d.index.get_level_values(xchoice)]
            d = d.reset_index(drop=True)
            d["index"] = index
            d = d.set_index("index")

            if not xlabels:
                X = index
                xset = xset.union(set(X))
            else:
                X = [x for x in xlabels if x in d.index.values]

            column = feature if feature in df else f"{feature}_m"
            Y.append([d.loc[x, column] for x in X])

            if dim != 1:
                X = [x**dim for x in X]

        ax.fill_between(X,Y[0], Y[1], facecolor=color, alpha=0.8)
        # ax.plot(X, Y, c=color, marker=marker, ms=5, fillstyle="none")


    # xnames = sorted(list(xset)) if not xlabels else xlabels
    # xticks = [x**dim for x in xnames]
    # plt.xticks(xticks, xnames)



f, ax = plt.subplots()
SMALL_SIZE = 13
MEDIUM_SIZE = 16
BIGGER_SIZE = 14

plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
plt.rc('axes', titlesize=SMALL_SIZE)     # fontsize of the axes title
plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('legend', fontsize=SMALL_SIZE)    # legend fontsize
plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title
# csv_names =[
#     # "simulations/cartesius/data/mwpm_toric_3d.csv",
#     # "simulations/cartesius/data/uf_toric_3d.csv",
#     "simulations/cartesius/data/eg_toric_3d.csv",
# ]
# plot_compare(ax, csv_names, "l", [], [], "time", 3)
Lrange = [8, 10, 12, 14, 16, 18, 20, 22, 24, 28, 32, 36, 40]
plot_compare(ax, "C3", ["simulations/cartesius/data/mwpm_toric_3d.csv"], "l", [0.027, 0.028, 0.029, 0.03, 0.031], Lrange, "time", 3)
plot_compare(ax, "C0", ["simulations/cartesius/data/uf_toric_3d.csv"], "l", [0.025, 0.026, 0.027, 0.028, 0.029], Lrange, "time", 3)
plot_compare(ax, "C2", ["simulations/cartesius/data/eg_toric_3d.csv"], "l", [0.02733, 0.02767, 0.02833, 0.02867, 0.02933, 0.02967], Lrange, "time", 3)


legend_elements = [
    Patch(facecolor="C3", label='MWPM', alpha=0.8),
    Patch(facecolor="C0", label='UF', alpha=0.8),
    Patch(facecolor="C2", label='UFBB', alpha=0.8),
]

plot_style(ax, "", "System size (N qubits)", "Average time per iteration")



ax.add_artist(plt.legend(handles=legend_elements, loc="upper right"))
plt.show()
f.savefig("time.pdf", transparent=True, format="pdf")
