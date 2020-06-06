import sys
sys.path.insert(0, '..')

import matplotlib.pyplot as plt
from plot_threshold import plot_multiple, plot_sequential
from thesis_style import latex_style


save=False
show=True

latex_style(0.5, 1)
output = "mwpm_toric_2d"
print("\n{}".format(output))
fig, ax = plot_multiple([output])
fig, ax = plot_multiple([output],modified_ansatz=True)
if save: fig.savefig("/home/watermarkhu/mep/mep-thesis/pgfplots/threshold_{}.pgf".format(output))
f0, f1, th = plot_sequential(
    "/home/watermarkhu/mep/oop_surface_code/cartesiusdata/{}.csv".format(output))
if save: f1.savefig("/home/watermarkhu/mep/mep-thesis/pgfplots/threshold_{}_seq.pgf".format(output))


output = "mwpm_planar_2d"
print("\n{}".format(output))
fig, ax = plot_multiple([output])
f0, f1, th = plot_sequential(
    "/home/watermarkhu/mep/oop_surface_code/cartesiusdata/{}.csv".format(output))
if save: fig.savefig("/home/watermarkhu/mep/mep-thesis/pgfplots/threshold_{}.pgf".format(output))


output = "mwpm_toric_3d"
print("\n{}".format(output))
fig, ax = plot_multiple([output])
f0, f1, th = plot_sequential(
    "/home/watermarkhu/mep/oop_surface_code/cartesiusdata/{}.csv".format(output))
if save: fig.savefig("/home/watermarkhu/mep/mep-thesis/pgfplots/threshold_{}.pgf".format(output))


output = "mwpm_planar_3d"
print("\n{}".format(output))
fig, ax = plot_multiple([output])
f0, f1, th = plot_sequential(
    "/home/watermarkhu/mep/oop_surface_code/cartesiusdata/{}.csv".format(output))
if save: fig.savefig("/home/watermarkhu/mep/mep-thesis/pgfplots/threshold_{}.pgf".format(output))

plt.show()
