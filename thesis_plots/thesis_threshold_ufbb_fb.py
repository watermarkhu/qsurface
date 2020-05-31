from thesis_style import *
from thesis_comp_threshold import comp_thresholds
from plot_threshold import plot_sequential
import matplotlib.pyplot as plt
import sys
sys.path.insert(0, '..')



save = 0
show = 1


# latex_style(0.32, 1.8)

for i in range(11):
    output = "ufbb_toric_2d_fb{:02d}".format(i)
    if i == 5:
        output = "ufbb_toric_2d"

    print("\n{}\n".format(output))
    f0, f1, th = plot_sequential("/home/watermarkhu/mep/oop_surface_code/cartesiusdata/{}.csv".format(output),
                                latts=[8+8*i for i in range(8)],
                                probs=[round(0.099 + i*0.0005, 5) for i in range(11)])

    f0.axes[0].set_xlim(0.099, 0.104)
    f0.axes[0].set_ylim(0.62, 0.82)
    f1.axes[0].set_xlim(0.0985, 0.104)
    f1.axes[0].set_ylim(0.71, 0.78)

    if i == 5:
        output = "ufbb_toric_2d_fb05"
    if save:
        f0.savefig("/home/watermarkhu/mep/mep-thesis/pgfplots/threshold_{}.pgf".format(output))
        f1.savefig("/home/watermarkhu/mep/mep-thesis/pgfplots/threshold_{}_seq.pgf".format(output))
    else:
        f0.axes[0].set_title(output)
        f1.axes[0].set_title(output)

if show: plt.show()
