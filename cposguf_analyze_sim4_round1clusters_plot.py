from collections import defaultdict as dd
import cposguf_cluster_actions as cca
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import matplotlib as mpl
import pickling as pk
import os
import numpy as np
mpl.rcParams["savefig.directory"] = os.chdir(os.getcwd())


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


def d0(): return [0,0]
def d1(): return [[0,0], [0,0]]
def d2(): return dd(d1)


data = pk.load_obj("sim4_r1ctrue_data_gauss12_44-c1_5")
lrange = [8, 12, 16, 20, 24, 28, 32, 36, 40, 44]
prange = [(90 + i)/1000 for i in range(21)]
plotn = [8 + i for i in range(2)]

####################################

def sort_data(data, type=None):
    if type == None:
        sortdata = sorted(data.items(),
            key=lambda kv:
            sum([v1[0] + v2[0] for v1, v2 in list(kv[1].values())]),
            reverse = True
        )
    elif type in data:
        sortdata = sorted(data.items(),
            key=lambda kv:
            sum([v[type][0] for v in list(kv[1].values())]),
            reverse = True
        )
    else:
        raise(KeyError)
    return sortdata

sdp = sort_data(data["data_p"])
snp = sort_data(data["data_n"])
countn, countp = data["countn"], data["countp"]


################################

fig0 = plt.figure()
grid = plt.GridSpec(5, len(plotn), wspace=0.1, hspace=1)
for i, cnum in enumerate(plotn):
    ax = plt.subplot(grid[0, i])
    cca.plot_cluster(sdp[i][0], 2, 2, ax=ax)
    ax.set_title(str(cnum))

ax = plt.subplot(grid[1:, :])

clms = np.zeros((2,len(plotn)))
clmt = dd(list)

for j, l in enumerate(lrange):
    for k, p in enumerate(prange):
        oc, (nc0, nc1) = 0, countp[(l, p)]
        (no0, _), (no1, _) = sdp[plotn[0]][1][(l, p)]
        for i, cnum in enumerate(plotn):
            omu, ova = clms[0][i], clms[1][i]
            (mu0, va0), (mu1, va1) = sdp[cnum][1][(l, p)]
            clms[0][i] = (oc*omu + nc0*mu0/no0 + nc1*mu1/no1)/(oc+nc0+nc1)
            clms[1][i] = (oc*(omu**2 + ova) + nc0*(mu0**2 + va0)/no0**2 + nc1*(mu1**2 + va1)/no1**2)/(oc + nc0 + nc1) - clms[0][i]**2
            clmt[(l, p)].append((nc0*mu0/no0 + nc1*mu1/no1)/(nc0+nc1))
        oc += nc0 + nc1

ax.set_title("Normalized averaged occurance rate of R1-clusters")
ax.set_xlabel("Cluster #")
ax.set_ylabel("Occurance rate")
plt.errorbar(plotn, clms[0], np.sqrt(clms[1]), elinewidth=1, capsize=2, color="k", ls=":")
plt.show()


################################

rtmt = dd(list)
fig = plt.figure()
grid = plt.GridSpec(len(plotn), 10, wspace=0.8, hspace=0.5)

for i, cnum in enumerate(plotn):

    ax = plt.subplot(grid[i, 0])
    ax.set_ylabel(str(cnum))
    cca.plot_cluster(sdp[cnum][0], 2, 2, ax=ax)
    ax0 = plt.subplot(grid[i, 1:4])
    plt.ylim(0.9, 1.1)
    ax0.axhline(y=1, color="k", ls="--", lw=0.5)
    clear_ax(i, len(plotn), "p")
    ax1 = plt.subplot(grid[i, 4:7])
    plt.ylim(0.75, 1.25)
    ax1.axhline(y=1, color="k", ls="--", lw=0.5)
    clear_ax(i, len(plotn), "n")
    ax2 = plt.subplot(grid[i, 7:])
    plt.ylim(0.75, 1.25)
    ax2.axhline(y=1, color="k", ls="--", lw=0.5)
    clear_ax(i, len(plotn), "norm n")

    for j, l, in enumerate(lrange):
        color="C{}".format(j % 10)

        pratio, prange2, pavgc = [], [], []
        for k, p in enumerate(prange):
            (mt, vt), (ml, vl) = sdp[cnum][1][(l, p)]
            nt, nl = countp[(l, p)]
            prange2.append(p*100)
            pratio.append(mt-ml)
            pavgc.append((nt + nl)/2)
            rtmt[(l, p)].append(mt/ml)

        nrange = sorted([n for _,n in snp[cnum][1].keys()])
        nratio, nrange2, navgc = [], [], []
        for n in nrange:
            (mt, vt), (ml, vl) = snp[cnum][1][(l, n)]
            nt ,nl = countn[(l, n)]
            if mt > 0 and ml > 0 and nt> 500:
                nrange2.append(n)
                nratio.append(mt/ml)
                navgc.append((nt + nl)/2)

        nrange3 = []
        for n in nrange2:
            nrange3.append((n-nrange2[0])/(nrange2[-1] - nrange2[0]))

        for prn, prt, pac in zip(prange2, pratio, pavgc):
            ax0.scatter(prn, prt, 1.5, color=color, alpha=pac/max(pavgc))
        for nrn0, nrn1, nrt, nac in zip(nrange2, nrange3, nratio, navgc):
            ax1.scatter(nrn0, nrt, 1.5, color=color, alpha=nac/max(navgc))
            ax2.scatter(nrn1, nrt, 1.5, color=color, alpha=nac/max(navgc))

        # ax0.plot(prange2, pratio, color=color, ls=":")
        # ax1.plot(nrange2, nratio, color=color, ls=":")
        # ax2.plot(nrange3, nratio, color=color, ls=":")#, alpha = 1-0.2*i)


custom_lines = [Line2D([0], [0], color="C{}".format(i % 10), label=str(c)) for i, c in enumerate(lrange)]
fig.legend(handles=custom_lines, bbox_to_anchor=(0.97, 0.55))
plt.show()


tldata = {
    "tl_ratio_p": rtmt,
    "norm_avg_occ_p": clmt
    }

# pk.save_obj(tldata, "sim4_tldata")


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
