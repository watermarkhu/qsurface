import sys
sys.path.insert(0, '..')

import matplotlib.pyplot as plt
from plot_threshold import plot_multiple, plot_sequential
from compare_heuristics import latex_style

latex_style(0.5, 1)

save = False
show = True

#DUF 
output = "duf_toric_2d"
print("\n{}".format(output))
fig, ax = plot_multiple([output])
if save: fig.savefig("/home/watermarkhu/mep/mep-thesis/pgfplots/threshold_{}.pgf".format(output))

output = "duf_planar_2d"
print("\n{}".format(output))
fig, ax = plot_multiple([output], latts=[8+8*i for i in range(8)])
if save: fig.savefig("/home/watermarkhu/mep/mep-thesis/pgfplots/threshold_{}.pgf".format(output))


output = "duf_toric_3d"
print("\n{}".format(output))
fig, ax = plot_multiple([output])
if save: fig.savefig("/home/watermarkhu/mep/mep-thesis/pgfplots/threshold_{}.pgf".format(output))

output = "duf_planar_3d"
print("\n{}".format(output))
fig, ax = plot_multiple([output])
if save: fig.savefig("/home/watermarkhu/mep/mep-thesis/pgfplots/threshold_{}.pgf".format(output))


if show():
    plt.show()       
