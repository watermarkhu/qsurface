import sys
sys.path.insert(0, '..')

import matplotlib.pyplot as plt
from plot_threshold import plot_multiple, plot_sequential
from compare_heuristics import latex_style

latex_style(0.5, 1)

save = 1
show = 0

#DBUF
output = "dbuf_toric_2d"
print("\n{}".format(output))
fig, ax = plot_multiple([output], latts=[8+8*i for i in range(8)])
if save: fig.savefig("/home/watermarkhu/mep/mep-thesis/pgfplots/threshold_{}.pgf".format(output))
f0, f1, th = plot_sequential(
    "/home/watermarkhu/mep/oop_surface_code/cartesiusdata/{}.csv".format(output), latts=[8+8*i for i in range(8)])
if save: f1.savefig("/home/watermarkhu/mep/mep-thesis/pgfplots/threshold_{}_seq.pgf".format(output))

output = "dbuf_planar_2d"
print("\n{}".format(output))
fig, ax = plot_multiple([output], latts=[8+8*i for i in range(8)])
if save: fig.savefig("/home/watermarkhu/mep/mep-thesis/pgfplots/threshold_{}.pgf".format(output))

# output = "dbuf_toric_2d_large"
# print("\n{}".format(output))
# fig, ax = plot_multiple([output], latts=[72+8*i for i in range(8)])
# if save: fig.savefig("/home/watermarkhu/mep/mep-thesis/pgfplots/threshold_{}.pgf".format(output))

# output = "dbuf_planar_2d_large"
# print("\n{}".format(output))
# fig, ax = plot_multiple([output], latts=[72+8*i for i in range(8)])
# if save: fig.savefig("/home/watermarkhu/mep/mep-thesis/pgfplots/threshold_{}.pgf".format(output))


output = "dbuf_toric_3d"
print("\n{}".format(output))
fig, ax = plot_multiple([output], latts=[8+4*i for i in range(8)])
if save: fig.savefig("/home/watermarkhu/mep/mep-thesis/pgfplots/threshold_{}.pgf".format(output))

output = "dbuf_planar_3d"
print("\n{}".format(output))
fig, ax = plot_multiple([output], latts=[8+4*i for i in range(8)])
if save: fig.savefig("/home/watermarkhu/mep/mep-thesis/pgfplots/threshold_{}.pgf".format(output))


if show:
    plt.show()       
