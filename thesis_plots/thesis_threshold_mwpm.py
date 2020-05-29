import sys
sys.path.insert(0, '..')

import matplotlib.pyplot as plt
from plot_threshold import plot_multiple
from thesis_style import latex_style

latex_style(0.5, 1)
output = "threshold_mwpm_toric_2d"
print("\n{}".format(output))
fig, ax = plot_multiple(["mwpm_toric_2d"])
# ax.set_ylim(0.62, 0.83)
plt.savefig("/home/watermarkhu/mep/mep-thesis/pgfplots/{}.pgf".format(output))

output = "threshold_mwpm_planar_2d"
print("\n{}".format(output))
fig, ax = plot_multiple(["mwpm_planar_2d"])
# ax.set_ylim(0.72, 0.93)
plt.savefig("/home/watermarkhu/mep/mep-thesis/pgfplots/{}.pgf".format(output))


output = "threshold_mwpm_toric_3d"
print("\n{}".format(output))
fig, ax = plot_multiple(["mwpm_toric_3d"])
# ax.set_ylim(0.73, 1)
plt.savefig("/home/watermarkhu/mep/mep-thesis/pgfplots/{}.pgf".format(output))


output = "threshold_mwpm_planar_3d"
print("\n{}".format(output))
fig, ax = plot_multiple(["mwpm_planar_3d"])
# ax.set_ylim(0.73, 1)
plt.savefig("/home/watermarkhu/mep/mep-thesis/pgfplots/{}.pgf".format(output))
plt.show()
