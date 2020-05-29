import sys
sys.path.insert(0, '..')

import matplotlib.pyplot as plt
from plot_threshold import plot_multiple
from compare_heuristics import latex_style

latex_style(0.5, 1)


# SUF 
output = "threshold_suf_toric_2d"
print("\n{}".format(output))
fig, ax = plot_multiple(["suf_toric_2d"])
plt.savefig("/home/watermarkhu/mep/mep-thesis/pgfplots/{}.pgf".format(output))

output = "threshold_suf_planar_2d"
print("\n{}".format(output))
fig, ax = plot_multiple(["suf_planar_2d"])
plt.savefig("/home/watermarkhu/mep/mep-thesis/pgfplots/{}.pgf".format(output))


output = "threshold_suf_toric_3d"
print("\n{}".format(output))
fig, ax = plot_multiple(["suf_toric_3d"])
plt.savefig("/home/watermarkhu/mep/mep-thesis/pgfplots/{}.pgf".format(output))


output = "threshold_suf_planar_3d"
print("\n{}".format(output))
fig, ax = plot_multiple(["suf_planar_3d"])
plt.savefig("/home/watermarkhu/mep/mep-thesis/pgfplots/{}.pgf".format(output))


#DUF 
output = "threshold_duf_toric_2d"
print("\n{}".format(output))
fig, ax = plot_multiple(["duf_toric_2d"])
plt.savefig("/home/watermarkhu/mep/mep-thesis/pgfplots/{}.pgf".format(output))

output = "threshold_duf_planar_2d"
print("\n{}".format(output))
fig, ax = plot_multiple(["duf_planar_2d"], latts=[8+8*i for i in range(8)])
plt.savefig("/home/watermarkhu/mep/mep-thesis/pgfplots/{}.pgf".format(output))


output = "threshold_duf_toric_3d"
print("\n{}".format(output))
fig, ax = plot_multiple(["duf_toric_3d"])
plt.savefig("/home/watermarkhu/mep/mep-thesis/pgfplots/{}.pgf".format(output))

output = "threshold_duf_planar_3d"
print("\n{}".format(output))
fig, ax = plot_multiple(["duf_planar_3d"])
plt.savefig("/home/watermarkhu/mep/mep-thesis/pgfplots/{}.pgf".format(output))


# #SBUF
output = "threshold_sbuf_toric_2d"
print("\n{}".format(output))
fig, ax = plot_multiple(["sbuf_toric_2d"])
plt.savefig("/home/watermarkhu/mep/mep-thesis/pgfplots/{}.pgf".format(output))

output = "threshold_sbuf_planar_2d"
print("\n{}".format(output))
fig, ax = plot_multiple(["sbuf_planar_2d"], latts=[8+8*i for i in range(8)])
plt.savefig("/home/watermarkhu/mep/mep-thesis/pgfplots/{}.pgf".format(output))

output = "threshold_sbuf_toric_3d"
print("\n{}".format(output))
fig, ax = plot_multiple(["sbuf_toric_3d"])
plt.savefig("/home/watermarkhu/mep/mep-thesis/pgfplots/{}.pgf".format(output))

output = "threshold_sbuf_planar_3d"
print("\n{}".format(output))
fig, ax = plot_multiple(["sbuf_planar_3d"])
plt.savefig("/home/watermarkhu/mep/mep-thesis/pgfplots/{}.pgf".format(output))


#DBUF
output = "threshold_dbuf_toric_2d"
print("\n{}".format(output))
fig, ax = plot_multiple(["dbuf_toric_2d"], latts=[8+8*i for i in range(8)])
plt.savefig("/home/watermarkhu/mep/mep-thesis/pgfplots/{}.pgf".format(output))

output = "threshold_dbuf_planar_2d"
print("\n{}".format(output))
fig, ax = plot_multiple(["dbuf_planar_2d"], latts=[8+8*i for i in range(8)])
plt.savefig("/home/watermarkhu/mep/mep-thesis/pgfplots/{}.pgf".format(output))

output = "threshold_dbuf_toric_2d_large"
print("\n{}".format(output))
fig, ax = plot_multiple(["dbuf_toric_2d"], latts=[72+8*i for i in range(8)])
plt.savefig("/home/watermarkhu/mep/mep-thesis/pgfplots/{}.pgf".format(output))

output = "threshold_dbuf_planar_2d_large"
print("\n{}".format(output))
fig, ax = plot_multiple(["dbuf_planar_2d"], latts=[72+8*i for i in range(8)])
plt.savefig("/home/watermarkhu/mep/mep-thesis/pgfplots/{}.pgf".format(output))


output = "threshold_dbuf_toric_3d"
print("\n{}".format(output))
fig, ax = plot_multiple(["dbuf_toric_3d"], latts=[8+4*i for i in range(8)])
plt.savefig("/home/watermarkhu/mep/mep-thesis/pgfplots/{}.pgf".format(output))

output = "threshold_dbuf_planar_3d"
print("\n{}".format(output))
fig, ax = plot_multiple(["dbuf_planar_3d"], latts=[8+4*i for i in range(8)])
plt.savefig("/home/watermarkhu/mep/mep-thesis/pgfplots/{}.pgf".format(output))
