from thesis_style import *
from thesis_comp_threshold import comp_thresholds
from plot_threshold import plot_ufbb
import matplotlib.pyplot as plt
import sys
sys.path.insert(0, '..')


latex_style(1)
output = "threshold_ufbb_toric_2d_full"
print("\n{}\n".format(output))
f0, f1, th = plot_ufbb("/home/watermarkhu/mep/oop_surface_code/cartesiusdata/ufbb_toric_2d.csv")
f0.savefig("/home/watermarkhu/mep/mep-thesis/pgfplots/{}.pgf".format(output))

latex_style(0.5, 1)
output = "threshold_ufbb_toric_2d_short"
print("\n{}\n".format(output))
f0, f1, th = plot_ufbb("/home/watermarkhu/mep/oop_surface_code/cartesiusdata/ufbb_toric_2d.csv",
                   probs=[round(0.099 + i*0.0005, 5) for i in range(11)])
f0.savefig("/home/watermarkhu/mep/mep-thesis/pgfplots/{}.pgf".format(output))
f1.savefig("/home/watermarkhu/mep/mep-thesis/pgfplots/{}_seq.pgf".format(output))

latex_style(1)
output = "threshold_ufbb_toric_2d_comp"
print("\n{}\n".format(output))
f2 = comp_thresholds([8+8*i for i in range(8)],"toric_2d", ['MWPM', "DBUF"], th)
f2.savefig("/home/watermarkhu/mep/mep-thesis/pgfplots/{}.pgf".format(output))





latex_style(1)
output = "threshold_ufbb_planar_2d_full"
print("\n{}\n".format(output))
f0, f1, th = plot_ufbb("/home/watermarkhu/mep/oop_surface_code/cartesiusdata/ufbb_planar_2d.csv")
f0.savefig("/home/watermarkhu/mep/mep-thesis/pgfplots/{}.pgf".format(output))

latex_style(0.5, 1)
output = "threshold_ufbb_planar_2d_short"
print("\n{}\n".format(output))
f0, f1, th = plot_ufbb("/home/watermarkhu/mep/oop_surface_code/cartesiusdata/ufbb_planar_2d.csv",
                   probs=[round(0.095 + i*0.0005, 5) for i in range(13)])
f0.savefig("/home/watermarkhu/mep/mep-thesis/pgfplots/{}.pgf".format(output))
f1.savefig("/home/watermarkhu/mep/mep-thesis/pgfplots/{}_seq.pgf".format(output))

latex_style(1)
output = "threshold_ufbb_planar_2d_comp"
print("\n{}\n".format(output))
f2 = comp_thresholds([8+8*i for i in range(8)],"planar_2d", ['MWPM', "DBUF"], th)
f2.savefig("/home/watermarkhu/mep/mep-thesis/pgfplots/{}.pgf".format(output))






output = "threshold_ufbb_toric_3d_full"
print("\n{}\n".format(output))
f0, f1, th = plot_ufbb("/home/watermarkhu/mep/oop_surface_code/cartesiusdata/ufbb_toric_3d.csv",
                   latts=[8+4*i for i in range(8)])
f0.savefig("/home/watermarkhu/mep/mep-thesis/pgfplots/{}.pgf".format(output))

latex_style(0.5, 1)
output = "threshold_ufbb_toric_3d_short"
print("\n{}\n".format(output))
f0, f1, th = plot_ufbb("/home/watermarkhu/mep/oop_surface_code/cartesiusdata/ufbb_toric_3d.csv", 
                    latts=[8+4*i for i in range(8)],
                    probs=[round(0.026 + i/3000, 5) for i in range(13)])
f0.savefig("/home/watermarkhu/mep/mep-thesis/pgfplots/{}.pgf".format(output))
f1.savefig("/home/watermarkhu/mep/mep-thesis/pgfplots/{}_seq.pgf".format(output))

latex_style(1)
output = "threshold_ufbb_toric_3d_comp"
print("\n{}\n".format(output))
f2 = comp_thresholds([8+8*i for i in range(8)], "toric_3d", ['MWPM', "DBUF"], th)
f2.savefig("/home/watermarkhu/mep/mep-thesis/pgfplots/{}.pgf".format(output))






latex_style(1)
output = "threshold_ufbb_planar_3d_full"
print("\n{}\n".format(output))
f0, f1, th = plot_ufbb(
    "/home/watermarkhu/mep/oop_surface_code/cartesiusdata/ufbb_planar_3d.csv", latts=[8+4*i for i in range(8)])
f0.savefig("/home/watermarkhu/mep/mep-thesis/pgfplots/{}.pgf".format(output))

latex_style(0.5, 1)
output = "threshold_ufbb_planar_3d_short"
print("\n{}\n".format(output))
f0, f1, th = plot_ufbb("/home/watermarkhu/mep/oop_surface_code/cartesiusdata/ufbb_planar_3d.csv",
            latts=[8+4*i for i in range(8)],
            probs=[round(0.024 + i/3000, 5) for i in range(13)])
f0.savefig("/home/watermarkhu/mep/mep-thesis/pgfplots/{}.pgf".format(output))
f1.savefig("/home/watermarkhu/mep/mep-thesis/pgfplots/{}_seq.pgf".format(output))

latex_style(1)
output = "threshold_ufbb_planar_3d_comp"
print("\n{}\n".format(output))
f2 = comp_thresholds([8+8*i for i in range(8)],"planar_3d", ['MWPM', "DBUF"], th)
f2.savefig("/home/watermarkhu/mep/mep-thesis/pgfplots/{}.pgf".format(output))


plt.show()
