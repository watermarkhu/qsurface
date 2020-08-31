from compare_heuristics import plot_compare, plot_compare2, latex_style, get_csvdir
from thesis_style import *
from thesis_comp_threshold import plot_thresholds
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from collections import defaultdict
from scipy import optimize
import numpy as np
import math
import sys
sys.path.insert(0, '..')
from simulator.threshold.fit import fit_thresholds, get_fit_func
from simulator.threshold.sim import get_data, read_data

folder = "/home/watermarkhu/mep/tqe_paper_ufbb/tikzfigs/"
LS = dict(UFNS="-", MWPM="dashdot", DBUF="--")
LS2 = dict(UFNS="-", MWPM="dashdot", BDUF="--")
markers = dict(UFNS=None, MWPM=None, BDUF=None)
alpha=1
lw=1


def plot_sequential(
    file_name,
    ax0,
    ax1,
    idx="",
    latts=[],
    probs=[],
    lattices=None,
    ms=4,
    style="-",           # linestyles for data and fit
    plotn=1000,                  # number of points on x axis
    ylabel=True,
):

    fit_func = get_fit_func(False)
    data = read_data(file_name)

    if not latts:
        latts = sorted(list(set(data.index.get_level_values("L"))))
    '''
    apply fit and get parameter
    '''
    parlist = []
    for i in range(len(latts)-1):
        (fitL, fitp, fitN, fitt), par = fit_thresholds(
            data, False, latts[i:i+2], probs)
        parlist.append(par)
    print("\nFinal:")
    (fitL, fitp, fitN, fitt), par = fit_thresholds(
        data, False, latts, probs)

    '''
    Plot and fit thresholds for a given dataset. Data is inputted as four lists for L, P, N and t.
    '''

    LP = defaultdict(list)
    for L, P, N, T in zip(fitL, fitp, fitN, fitt):
        LP[L].append([P, N, T])

    if lattices is None:
        lattices = sorted(set(fitL))

    cmap = plt.get_cmap('tab20')
    colors = {lati: cmap(i) for i, lati in zip(np.linspace(0, 1, len(lattices)), lattices)}

    markerlist = get_markers()
    markers = {lati: markerlist[i % len(markerlist)]
               for i, lati in enumerate(lattices)}

    leg1, leg2 = [], []

    for i, lati in enumerate(lattices):
        fp, fN, fs = map(list, zip(*sorted(LP[lati], key=lambda k: k[0])))
        ft = [si / ni for si, ni in zip(fs, fN)]
        ax0.plot(
            [q*100 for q in fp], [y*100 for y in ft],
            color=colors[lati],
            ls="-",
            lw=lw,
            alpha=alpha,
            label="{}".format(lati),
        )

    DS = fit_func((par[0], 20), *par)
    print("DS = {}".format(DS))

    var = 0.0004
    for par, lati, laty in zip(parlist, latts[:-1], latts[1:]):

        X = np.linspace(par[0] - var, par[0] + var, plotn)
        ax1.plot(
            [x for x in X],
            [fit_func((x, lati), *par) for x in X],
            "-",
            lw=lw,
            color=colors[lati],
            alpha=alpha,
            ls=style,
        )
        ax1.plot(
            [x for x in X],
            [fit_func((x, laty), *par) for x in X],
            "-",
            lw=lw,
            color=colors[laty],
            alpha=alpha,
            ls=style,
        )

    thresholds = []
    for par, lati, laty in zip(parlist, latts[:-1], latts[1:]):
        pth = par[0]
        kc = fit_func((pth, 20), *par)
        thresholds.append([pth, kc, colors[lati], markers[laty]])
        ax1.plot(pth, kc, color=colors[lati], lw=lw,
                 marker=markers[laty], ms=ms, fillstyle="none")

    pname = r"$p_{th}$"
    kname = r"$k_d (\%)$"

    if ylabel:
        plot_style(ax0, "", r" $ p_Z $", r"$k_d (\%)$")
    else:
        plot_style(ax0, "", r" $ p_Z $")

    return f0, thresholds, colors


def comp_thresholds(ax, lattices, type, colors, linestyles, decoders=[], thdata=[], ylabel=None):

    legend_elements = []

    for decoder in decoders:
        data = read_data("/home/watermarkhu/mep/OpenSurfaceSim/cartesiusdata/{}_{}.csv".format(decoder.lower(), type))

        (fitL, fitp, fitN, fitt), par = fit_thresholds(
            data, False, latts=lattices)

        LP = defaultdict(list)
        for L, P, N, T in zip(fitL, fitp, fitN, fitt):
            LP[L].append([P, N, T])

        if lattices is None:
            lattices = sorted(set(fitL))

        
        markerlist = get_markers()
        markers = {lati: markerlist[i % len(markerlist)]
                for i, lati in enumerate(lattices)}

        leg1, leg2 = [], []

        for i, lati in enumerate(lattices):
            fp, fN, fs = map(list, zip(*sorted(LP[lati], key=lambda k: k[0])))
            ft = [si / ni for si, ni in zip(fs, fN)]
            ax.plot(
                [q*100 for q in fp], [y*100 for y in ft],
                color=colors[lati],
                ls=linestyles[decoder],
                lw=lw,
                alpha=alpha,
                label="{}".format(lati),
            )
    for i, (x, y, color, marker) in enumerate(thdata):
        ax.plot(x*100, y*100, "*", ms=5, color=color, marker=marker, lw=lw, fillstyle="none")

    if ylabel is None:
        ylabel = r"$k_d (\%)$"

    plot_style(ax, "", r" $ p_Z (\%)$", ylabel)


def threscompplot(
    file_name,
    title="",
    idx="",
    latts=[],
    probs=[],
    modified_ansatz=False,
    ax=None,                   # axis object of error fit plot
    lw=1,
    style="-",           # linestyles for data and fit
    leg=False,
    legendname="",
    legloc="lower left",
    yb=False,
    starti=0,
    **kwargs
):

    data = read_data(file_name)
    '''
    apply fit and get parameter
    '''
    (fitL, fitp, fitN, fitt), par = fit_thresholds(
        data, modified_ansatz, latts, probs)

    fit_func = get_fit_func(modified_ansatz)

    '''
    Plot and fit thresholds for a given dataset. Data is inputted as four lists for L, P, N and t.
    '''

    LP = defaultdict(list)
    for L, P, N, T in zip(fitL, fitp, fitN, fitt):
        LP[L].append([P, N, T])

    lattices = sorted(set(fitL))

    colors = {lati: f"C{(i+starti)%10}" for i, lati in enumerate(lattices)}
    markerlist = get_markers()
    markers = {lati: markerlist[(i+starti) % len(markerlist)]
               for i, lati in enumerate(lattices)}
    legend = []

    for i, lati in enumerate(lattices):
        fp, fN, fs = map(list, zip(*sorted(LP[lati], key=lambda k: k[0])))
        ft = [si / ni for si, ni in zip(fs, fN)]
        ax.plot(
            [q*100 for q in fp], [y*100 for y in ft],
            color=colors[lati],
            ls=style,
            lw=lw,
        )
        legend.append(Line2D(
            [0],
            [0],
            label="{}".format(lati),
            color=colors[lati],
            lw=lw,
        ))

    DS = fit_func((par[0], 20), *par)
    print("DS = {}".format(DS))

    pname = r"$p_{th}$"
    kname = r"Decoding rate $k_d$"

    if yb:
        plot_style(ax, title, r"$p_Z (\%)$", r"Decoding rate $k_d$", **kwargs)
    else:
        plot_style(ax, title, r"$p_Z (\%)$", "", **kwargs)

    if leg:
        legend = ax.legend(handles=legend, loc=legloc, ncol=2,
                           markerscale=1, fontsize="small", columnspacing=0.2, labelspacing=0.2, handletextpad=0.2, handlelength=0.5, numpoints=1, title=r"{}$L$".format(legendname), title_fontsize=8)
    return ax




latex_style(1.15,0.45)

f0, (ax0a, ax1) = plt.subplots(1, 2, gridspec_kw={'width_ratios': [1, 2]}, sharey = True, tight_layout = True)

ax0b = plt.axes([0.11, 0.2, .2, .3])
ax0b.axes.xaxis.set_visible(False)
ax0b.axes.yaxis.set_visible(False)
plt.tight_layout()
f0, th, colors, = plot_sequential("/home/watermarkhu/mep/OpenSurfaceSim/cartesiusdata/ufbb_toric_2d.csv", ax0a, ax0b,probs=[round(0.099 + i*0.0005, 4) for i in range(11)])
comp_thresholds(ax1, [8+8*i for i in range(8)], "toric_2d", colors, LS, ['MWPM', "DBUF"], th, ylabel="")

leg1 = [Line2D([0], [0], lw=lw, ls="-", color=color, label=name) for name, color in colors.items()]
leg2 = [Line2D([0], [0], lw=lw, ls=style, color="k", label=name) for name, style in LS2.items()]
plt.sca(ax1)
ax1.add_artist(plt.legend(handles=leg1, loc="lower left", ncol=3, **
    legend_style(handletextpad=0.2, handlelength=1, columnspacing=0.5), title=r"$L$", title_fontsize=8))
ax1.add_artist(plt.legend(handles=leg2, loc="upper right"))

ax0a.text(10.32, 81, r"\emph{(a)}")
ax0b.text(0.1017, 0.78, r"\emph{(b)}")
ax1.text(9.83, 81, r"\emph{(c)}")

# ### comp ### 


# latex_style(scale=0.55, y=0.9)
# f2, ax2a = plt.subplots()

# C1 = dict(MWPM="C0", UFNS="C0", BDUF="C0")
# C2 = dict(MWPM="C3", UFNS="C3", BDUF="C3")

# l = [8+i*8 for i in range(8)]
# names = get_csvdir(["mwpm_toric_2d", "ufbb_toric_2d", "dbuf_toric_2d"])
# plot_compare2(["MWPM", "UFNS", "BDUF"], names, "l", [
#     0.1], l, "weight", dim=2, yname=r"$ |\mathcal{C}|/ |\mathcal{C}_{MWPM}| $", normy=0.1, show_legend=False, show_normline=False, colors=C1, linestyles=LS2, markers=markers, gridcolor="C0")

# ax2b = ax2a.twinx()
# names = get_csvdir(["mwpm_toric_2d", "ufbb_toric_2d", "dbuf_toric_2d"])
# plot_compare(["MWPM", "UFNS", "BDUF"],
#              names, "l", [0.1], l, "time", dim=2, yname="Average running time (s)", normy=0.1, show_legend=False, colors=C2, linestyles=LS2, markers=markers, gridcolor="C3")

# ax2a.set_ylim(1,1.07)
# ax2a.yaxis.label.set_color("C0")
# ax2b.yaxis.label.set_color("C3")

# leg = [Line2D([0], [0], ls=style, color="k", label=name, lw=lw) for name, style in LS.items()]
# plt.legend(handles=leg, loc="upper left")
# plt.tight_layout()


# # ### comparison ###



D2 = [
    "/home/watermarkhu/mep/OpenSurfaceSim/cartesiusdata/delfosse_2d_uf.csv",
    "/home/watermarkhu/mep/OpenSurfaceSim/cartesiusdata/delfosse_2d_dbuf.csv",
    "/home/watermarkhu/mep/OpenSurfaceSim/cartesiusdata/delfosse_2d_ufbb.csv",
    "/home/watermarkhu/mep/OpenSurfaceSim/cartesiusdata/delfosse_2d_mwpm.csv",
]

D3 = [
    "/home/watermarkhu/mep/OpenSurfaceSim/cartesiusdata/delfosse_3d_uf.csv",
    "/home/watermarkhu/mep/OpenSurfaceSim/cartesiusdata/delfosse_3d_dbuf.csv",
    "/home/watermarkhu/mep/OpenSurfaceSim/cartesiusdata/delfosse_3d_ufbb.csv",
    "/home/watermarkhu/mep/OpenSurfaceSim/cartesiusdata/delfosse_3d_mwpm.csv",
]
ufstyle = (0, (3, 1, 1, 1, 1))

# latex_style(1.15, 0.45)
# (f3, axes3) = plt.subplots(1, 4, sharey=True, tight_layout=True)
# axes3 = list(axes3)
# for i in range(4):
#     axes3.append(axes3[i].twiny())

# threscompplot(D2[0], "UF",  ax=axes3[0], gridstyle="-", gridwidth=0.6, yb=1, leg=1, legloc="lower left")
# threscompplot(D2[1], "BDUF",        ax=axes3[1], gridstyle="-", gridwidth=0.6)
# threscompplot(D2[2], "UFNS",        ax=axes3[2], gridstyle="-", gridwidth=0.6)
# threscompplot(D2[3], "MWPM",        ax=axes3[3], gridstyle="-", gridwidth=0.6)
# threscompplot(D3[0], "", gridwidth=0.6, starti=6, ax=axes3[4], yb=1, leg=1, legloc="upper right")
# threscompplot(D3[1], "", gridwidth=0.6, starti=6, ax=axes3[5])
# threscompplot(D3[2], "", gridwidth=0.6, starti=6, ax=axes3[6])
# threscompplot(D3[3], "", gridwidth=0.6, starti=6, ax=axes3[7])


latex_style(1.15, 0.5)
(f4, axes4) = plt.subplots(2, 4, sharey="row", tight_layout=True, gridspec_kw={'wspace': 0.1, 'hspace': 0.5})

threscompplot(D2[0], "UF", ax=axes4[0][0])
threscompplot(D2[1], "BDUF",       ax=axes4[0][1])
threscompplot(D2[2], "UFNS",       ax=axes4[0][2])
threscompplot(D2[3], "MWPM",       ax=axes4[0][3], yb=1, leg=1, legloc="lower left")
threscompplot(D3[0], "", starti=6, ax=axes4[1][0])
threscompplot(D3[1], "", starti=6, ax=axes4[1][1])
threscompplot(D3[2], "", starti=6, ax=axes4[1][2])
threscompplot(D3[3], "", starti=6, ax=axes4[1][3], yb=1, leg=1, legloc="lower left")

axes4[0][0].set_ylabel(r"$k_d (\%)$")
axes4[0][3].set_ylabel("Independent\nnoise")
axes4[0][3].yaxis.set_label_coords(1.4, 0.5)
axes4[1][0].set_ylabel(r"$k_d (\%)$")
axes4[1][3].set_ylabel("Phenomenological\nnoise")
axes4[1][3].yaxis.set_label_coords(1.4, 0.5)


'''
Compare matching weight
'''
keys = ["MWPM", "AUF", "DUF", "BAUF", "BDUF", "UFNS"]
markers = {key: None for key in keys}
linestyles = {
    "MWPM": "dashdot",
    "AUF":  "--",
    "DUF":  "--",
    "BAUF": "--",
    "BDUF": "--",
    "UFNS": "-"
}

colors = {
    "MWPM": "C3",
    "AUF":  "C1",
    "DUF":  "C4",
    "BAUF": "C9",
    "BDUF": "C0",
    "UFNS": "C2"
}

latex_style(scale=0.55, y=0.8)
f5, ax5 = plt.subplots(tight_layout=True)
l = [8+i*8 for i in range(8)]
names = get_csvdir(["mwpm_toric_2d", "suf_toric_2d", "duf_toric_2d",
                    "sbuf_toric_2d", "dbuf_toric_2d", "ufbb_toric_2d"])
latex_style(scale=0.55, y=0.9)
plot_compare2(keys, names, "l", [0.098], l, "weight", dim=2, yname=r"$ |\mathcal{C}|/ \min{|\mathcal{C}|} $", normy=0.1, markers=markers, colors=colors, linestyles=linestyles, show_normline=0)

'''
Compare computation time
'''


latex_style(scale=0.55, y=0.6)
f6, ax6 = plt.subplots()

keys = ["UFNS", "MWPM", "BDUF"]
names = get_csvdir(["ufbb_toric_2d", "mwpm_toric_2d", "dbuf_toric_2d"])
plot_compare(keys,
             names, "l", [0.1], l, "time", dim=2, yname="Mean time (s)", normy=0.1, show_legend=False, colors=colors, linestyles=linestyles, markers=markers)
leg = [Line2D([0], [0], ls=linestyles[key], color=colors[key], label=key, lw=lw) for key in keys]
plt.legend(handles=leg, loc="upper left")
plt.tight_layout()


'''
lowerror time
'''
latex_style(scale=0.55, y=1)
f8, axes = plt.subplots(3, 1, tight_layout=True, sharex=True, gridspec_kw={'wspace': 0, 'hspace': 0.1})

keys = ["UFNS", "MWPM", "BDUF"]
names = get_csvdir(["ufns_lowerror", "mwpm_lowerror", "bduf_lowerror"])

prange = [0.005, 0.012, 0.02]
xnames = ["", "", "L"]
for ax, p, x in zip(axes, prange, xnames):
    plt.sca(ax)
    plot_compare(keys,
                names, "l", [p], [6, 10, 14, 18], "time", dim=3, yname="", xname=x, show_legend=False, colors=colors, linestyles=linestyles, markers=markers)
    ax.annotate(r"$p_Z$={:.1f}\%".format(p*100), xy=(0.5, 0.9), xycoords='axes fraction',
                horizontalalignment='center', verticalalignment='top')
axes[1].set_ylabel("Mean time (s)")
leg = [Line2D([0], [0], ls=linestyles[key], color=colors[key], label=key, lw=lw) for key in keys]
axes[2].legend(handles=leg, loc="upper left")
plt.tight_layout()

# '''
# lowerror time and weight
# '''
# latex_style(scale=0.55, y=1)
# f9, axes = plt.subplots(3, 1, tight_layout=True, sharex=True, gridspec_kw={'wspace': 0, 'hspace': 0.1})
# taxes = [ax.twinx() for ax in axes]

# keys = ["UFNS", "MWPM", "BDUF"]
# names = get_csvdir(["ufns_lowerror", "mwpm_lowerror", "bduf_lowerror"])
# keys2 = ["MWPM", "UFNS", "BDUF"]
# names2 = get_csvdir(["mwpm_lowerror", "ufns_lowerror", "bduf_lowerror"])

# prange = [0.005, 0.012, 0.02]
# xnames = ["", "", "L"]
# for ax, tax, p, x in zip(axes, taxes, prange, xnames):
#     plt.sca(ax)
    
#     plot_compare(keys,
#                  names, "l", [p], [6, 10, 14, 18], "time", dim=3, yname="", xname=x, show_legend=False, colors=colors, linestyles=linestyles, markers=markers)
#     ax.annotate(r"$p_Z$={:.1f}\%".format(p*100), xy=(0.5, 0.9), xycoords='axes fraction',
#                 horizontalalignment='center', verticalalignment='top')
    
#     plt.sca(tax)
#     plot_compare2(keys2, names2, "l", [p], [6, 10, 14, 18], "weight", dim=3,
#                   yname=r"$ |\mathcal{C}|/ \min{|\mathcal{C}|} $", markers=markers, colors=colors, linestyles=linestyles, show_normline=0)

# axes[1].set_ylabel("Mean time (s)")
# leg = [Line2D([0], [0], ls=linestyles[key], color=colors[key], label=key, lw=lw) for key in keys]
# axes[2].legend(handles=leg, loc="upper left")
# plt.tight_layout()

'''
lowerror decoding rate
'''
latex_style(scale=0.55, y=0.6)
f7, ax7 = plt.subplots(tight_layout=True)

colors = {6:"C6", 10: "C7", 14:"C8", 18: "C9"}
linestyles = {"UFNS": "-", "MWPM": "dashdot", "BDUF": "--"} #, 'AUF': "dotted"}
comp_thresholds(ax7, [6, 10, 14, 18], "lowerror", colors, linestyles, ["UFNS", "MWPM", "BDUF"]) #, 'AUF'])
leg1 = [Line2D([0], [0], ls=ls, color="k", label=key, lw=lw) for key, ls in linestyles.items()]
leg2 = [Line2D([0], [0], ls="-", color=c, label=key, lw=lw) for key, c in colors.items()]
ax7.add_artist(plt.legend(handles=leg1, loc="lower center", columnspacing=0.2, handletextpad=0.2, handlelength=2))
ax7.add_artist(plt.legend(handles=leg2, loc="lower left", columnspacing=0.2, handletextpad=0.5, handlelength=2, title="L", title_fontsize=8))


plt.show()
# f0.savefig(folder + "threshold_ufbb.pdf")
# # f2.savefig(folder + "comp_ufbb_toric_2d_p98.pdf")
# # f3.savefig(folder + "threshold_comparison_dense.pdf")
# f4.savefig(folder + "threshold_comparison.pdf")
# f5.savefig(folder + "comp_matching_weight.pdf")
# f6.savefig(folder + "comp_time.pdf")
# f7.savefig(folder + "comp_lowerror.pdf")
# f8.savefig(folder + "comp_lowerror_time.pdf")
