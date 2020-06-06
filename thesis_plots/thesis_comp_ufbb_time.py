
from compare_heuristics import plot_compare, plot_compare2, get_csvdir, latex_style

latex_style(scale=0.5, y=1)

l = [8+i*8 for i in range(8)]

# 2D toric comp time uf

names = get_csvdir(["dbuf_toric_2d", "ufbb_toric_2d", "mwpm_toric_2d"])
plot_compare(["DBUF", "UFBB", "MWPM"],
             names, "l", [0.1], l, "time", dim=2, yname="Average running time (s)", normy=0.1, output="tcomp_ufbbmwpm_toric_2d_p98_norm")

names = get_csvdir(["dbuf_planar_2d", "ufbb_planar_2d", "mwpm_planar_2d"])
plot_compare(["DBUF", "UFBB", "MWPM"],
             names, "l", [0.1], l, "time", dim=2, yname="Average running time (s)", normy=0.1, output="tcomp_ufbbmwpm_planar_2d_p98_norm")


l = [8+i*4 for i in range(4)]
# 2D toric comp time uf
names = get_csvdir(["dbuf_toric_3d", "ufbb_toric_3d", "mwpm_toric_3d"])
plot_compare(["DBUF", "UFBB", "MWPM"],
             names, "l", [0.027], l, "time", dim=3, yname="Average running time (s)", output="tcomp_ufbbmwpm_toric_3d_p27_norm")

names = get_csvdir(["dbuf_planar_3d", "ufbb_planar_3d", "mwpm_planar_3d"])
plot_compare(["DBUF", "UFBB", "MWPM"],
             names, "l", [0.027], l, "time", dim=3, yname="Average running time (s)", output="tcomp_ufbbmwpm_planar_3d_p27_norm")

