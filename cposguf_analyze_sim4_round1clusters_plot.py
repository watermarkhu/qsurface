import pickle
from collections import defaultdict as dd
import cposguf_cluster_actions as cca
import matplotlib.pyplot as plt


def load_obj(name ):
    with open(name + '.pkl', 'rb') as f:
        return pickle.load(f)

def clear_ax(i, n, name=""):
    ax = plt.gca()
    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    if i != n-1:
        if i == 0:
            ax.set_title("tree/list occurence ratio vs " + name)
        ax.set_xticklabels([])
        ax.spines["bottom"].set_visible(False)
        ax.get_xaxis().set_ticks([])
    else:
        ax.set_xlabel(name)


def d1(): return [0,0]
def d2(): return dd(d1)

data = load_obj("sim4_r1c_data")

def sort_data(data, type=None):
    if type == None:
        sortdata = sorted(data.items(),
            key=lambda kv:
            sum([v1 + v2 for v1, v2 in list(kv[1].values())]),
            reverse = True
        )
    elif type in data:
        sortdata = sorted(data.items(),
            key=lambda kv:
            sum(kv[type]),
            reverse = True
        )
    else:
        raise(KeyError)
    return sortdata


sdp = sort_data(data["data_p"])
snp = sort_data(data["data_n"])

len(sdp)

countn, countp = data["countn"], data["countp"]

L = [8, 12]
LS = ["-", ":", "--"]
plotn=[0 + i for i in range(8)]

grid = plt.GridSpec(len(plotn), 5, wspace=0.4, hspace=0.3)

for i, cnum in enumerate(plotn):

    ax = plt.subplot(grid[i, 0])
    cca.plot_cluster(sdp[i][0], 3, 3, ax=ax)
    ax0=plt.subplot(grid[i, 1:3])
    ax0.axhline(y=1, color="k", ls="--")
    clear_ax(i, len(plotn), "p")
    ax1=plt.subplot(grid[i, 3:])
    ax1.axhline(y=1, color="k", ls="--")
    clear_ax(i, len(plotn), "norm n")


    for i, l, in enumerate(L):
        color="C{}".format(i % 10)

        prange = sorted([p for _,p in sdp[cnum][1].keys()])
        nrange = sorted([n for _,n in snp[cnum][1].keys()])

        pratio, prange2, perr = [], [], []
        for p in prange:
            rt, rl = sdp[cnum][1][(l, p)]
            nt, nl = countp[(l, p)]
            pt, pl = rt/nt, rl/nl
            var = abs(((1-pt)/(nt*pt) + (1-pl)/(nl*pl))**(1/2)*nt*pt/(nl*pl))
            prange2.append(p*100)
            pratio.append(pt/pl)
            perr.append(var)

        nratio, nrange2, nerr = [], [], []
        for n in nrange:
            rt, rl = snp[cnum][1][(l, n)]
            nt ,nl = countn[(l, n)]
            if rt > 500 and nt > 1000:
                pt, pl = rt/nt, rl/nl
                var = abs(((1-pt)/(nt*pt) + (1-pl)/(nl*pl))**(1/2)*nt*pt/(nl*pl))
                nrange2.append(n)
                nratio.append(pt/pl)
                nerr.append(var)

        nrange3 = []
        for n in nrange2:
            nrange3.append((n-nrange2[0])/(nrange2[-1] - nrange2[0]))

        ax0.errorbar(prange2, pratio, perr, color=color, ls=":", elinewidth=0.5, capsize=1)
        ax1.errorbar(nrange3, nratio, nerr, color=color, ls=":", elinewidth=0.5, capsize=1)

plt.show()

# fig = cca.plot_clusters(clusters, count, plotnum)
#
# folder = "../../../OneDrive - Delft University of Technology/MEP - thesis Mark/Simulations/cposguf_sim3_round1clusters/"
# file_name = "cposguf_sim3_L-"
# file_name += "None_p-" if l is None else "{0:d}_p-".format(l)
# file_name += "None" if p is None else "{0:.3f}".format(p)
# fname = folder + "figures/" + file_name + ".pdf"
# fig.savefig(fname, transparent=True, format="pdf", bbox_inches="tight")
# plt.close(fig)
#
# f = open(folder + "data/" + file_name + ".txt", "w")
# f.write("Count: " + str(count))
# for line in clusters:
#     f.write(str(line) + "\n")
# f.close()
