
from compare_heuristics import plot_compare, plot_compare2, get_csvdir, latex_style

latex_style(scale=0.5, y=1)

l = [8+i*8 for i in range(8)]

# 2D toric comp time uf
names = get_csvdir(["suf_toric_2d", "duf_toric_2d",
                    "sbuf_toric_2d", "dbuf_toric_2d"])
plot_compare(["SUF", "DUF", "SBUF", "DBUF"],
             names, "l", [0.098], l, "time", dim=2, yname="Average running time (s)", normy=0.1, output="tcomp_uf_toric_2d_p98_norm")

names = get_csvdir(["suf_planar_2d", "duf_planar_2d",
                    "sbuf_planar_2d", "dbuf_planar_2d"])
plot_compare(["SUF", "DUF", "SBUF", "DBUF"],
             names, "l", [0.098], l, "time", dim=2, yname="Average running time (s)", normy=0.1, output="tcomp_uf_planar_2d_p98_norm")


l = [8+i*4 for i in range(4)]
# 2D toric comp time uf
names = get_csvdir(["suf_toric_3d", "duf_toric_3d",
                    "sbuf_toric_3d", "dbuf_toric_3d"])
plot_compare(["SUF", "DUF", "SBUF", "DBUF"],
             names, "l", [0.027], l, "time", dim=3, yname="Average running time (s)", output="tcomp_uf_toric_3d_p27_norm")

names = get_csvdir(["suf_planar_3d", "duf_planar_3d",
                    "sbuf_planar_3d", "dbuf_planar_3d"])
plot_compare(["SUF", "DUF", "SBUF", "DBUF"],
             names, "l", [0.027], l, "time", dim=3, yname="Average running time (s)", output="tcomp_uf_planar_3d_p27_norm")

