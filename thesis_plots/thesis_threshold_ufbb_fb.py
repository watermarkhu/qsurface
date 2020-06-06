from thesis_style import *
from thesis_comp_threshold import comp_thresholds
from plot_threshold import plot_sequential
import matplotlib.pyplot as plt
import sys
sys.path.insert(0, '..')



save = 1
show = 1

blip = [4, 5, 6]
latex_style(1,0.6)

title = r"$f_{eq} = $"

(f1, axes1) = plt.subplots(1,len(blip), sharey=True, tight_layout=True)
(f2, axes2) = plt.subplots(1,len(blip), sharey=True, tight_layout=True)

axes = [[[f1, ax1], [f2, ax2]] for ax1, ax2 in zip(axes1, axes2)]

for i, ax in zip(blip, axes):
    output = "ufbb_toric_2d_fb{:02d}".format(i)
    if i == 5:
        output = "ufbb_toric_2d"


    print("\n{}\n".format(output))
    ylabel = True if i == blip[0] else False
    plot_sequential("/home/watermarkhu/mep/oop_surface_code/cartesiusdata/{}.csv".format(output),
                                latts=[8+8*i for i in range(8)],
                                probs=[round(0.099 + i*0.0005, 5) for i in range(11)], 
                                axes=ax, ylabel=ylabel)
    
    [[f1, ax1], [f2, ax2]] = ax

    ax1.set_title("{}{:.1f}".format(title, i/10))
    # ax2.set_title("{}{:.1f}".format(title, i/10))

    ax1.set_xlim(0.0985, 0.104)
    ax1.set_ylim(0.6, 0.83)
    ax2.set_xlim(0.0985, 0.104)
    ax2.set_ylim(0.71, 0.78)

if save:
    f1.savefig("/home/watermarkhu/mep/mep-thesis/pgfplots/threshold_ufbb_toric_2d_fb.pgf")
    f2.savefig("/home/watermarkhu/mep/mep-thesis/pgfplots/threshold_ufbb_toric_2d_fb_seq.pgf")

if show: plt.show()
