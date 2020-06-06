import sys
sys.path.insert(0, '..')

import matplotlib.pyplot as plt
from plot_threshold import plot_multiple, plot_sequential
from compare_heuristics import latex_style

latex_style(0.5, 1)

save = 0
show = 1

# #DBUF

# output = "ufbb_toric_2d"
# print("\n{}".format(output))
# fig, ax = plot_multiple([output], latts=[8+8*i for i in range(8)], 
#     probs=[round(0.099 + i*0.0005, 5) for i in range(11)])
# if save: fig.savefig("/home/watermarkhu/mep/mep-thesis/pgfplots/threshold_{}_small.pgf".format(output))

# output = "ufbb_planar_2d"
# print("\n{}".format(output))
# fig, ax = plot_multiple([output], latts=[8+8*i for i in range(8)],
#     probs=[round(0.096 + i*0.0005, 5) for i in range(11)])
# if save: fig.savefig("/home/watermarkhu/mep/mep-thesis/pgfplots/threshold_{}_small.pgf".format(output))


# output = "ufbb_toric_3d"
# print("\n{}".format(output))
# fig, ax = plot_multiple([output], latts=[8+4*i for i in range(5)],
#     probs=[round(0.027 + i/3000, 5) for i in range(10)])
# if save: fig.savefig("/home/watermarkhu/mep/mep-thesis/pgfplots/threshold_{}_small.pgf".format(output))

# output = "ufbb_planar_3d"
# print("\n{}".format(output))
# fig, ax = plot_multiple([output], latts=[8+4*i for i in range(5)],
#     probs=[round(0.025 + i/3000, 5) for i in range(10)])
# if save: fig.savefig("/home/watermarkhu/mep/mep-thesis/pgfplots/threshold_{}_small.pgf".format(output))



# output = "ufbb_toric_2d"
# print("\n{}".format(output))
# fig, ax = plot_multiple([output], latts=[72+8*i for i in range(4)], 
#     probs=[round(0.099 + i*0.0005, 5) for i in range(11)])
# if save: fig.savefig("/home/watermarkhu/mep/mep-thesis/pgfplots/threshold_{}_big.pgf".format(output))

# output = "ufbb_planar_2d"
# print("\n{}".format(output))
# fig, ax = plot_multiple([output], latts=[72+8*i for i in range(4)],
#     probs=[round(0.096 + i*0.0005, 5) for i in range(11)])
# if save: fig.savefig("/home/watermarkhu/mep/mep-thesis/pgfplots/threshold_{}_big.pgf".format(output))


output = "ufbb_toric_3d_e"
print("\n{}".format(output))
fig, ax = plot_multiple([output], latts=[28+4*i for i in range(5)],
    probs=[round(0.027 + i/3000, 5) for i in range(10)])
if save: fig.savefig("/home/watermarkhu/mep/mep-thesis/pgfplots/threshold_{}_big.pgf".format(output))

output = "ufbb_planar_3d_e"
print("\n{}".format(output))
fig, ax = plot_multiple([output], latts=[28+4*i for i in range(5)],
    probs=[round(0.025 + i/3000, 5) for i in range(10)])
if save: fig.savefig("/home/watermarkhu/mep/mep-thesis/pgfplots/threshold_{}_big.pgf".format(output))



if show:
    plt.show()       
