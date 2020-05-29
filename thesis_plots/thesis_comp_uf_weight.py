
from compare_heuristics import plot_compare, plot_compare2, latex_style, get_csvdir


l = [8+i*8 for i in range(8)]

# 2D toric comp weight uf
latex_style(scale=0.5,y=1)
names = get_csvdir(["suf_toric_2d", "duf_toric_2d",
                    "sbuf_toric_2d", "dbuf_toric_2d", "mwpm_toric_2d"])
plot_compare(["SUF", "DUF", "SBUF", "DBUF","MWPM"],
             names, "l", [0.098], l, "weight", dim=2, yname=r"$ |\mathcal{C}| $", normy=0.1, output="mwcomp_uf_toric_2d_p98_nnorm")

names = get_csvdir(["mwpm_toric_2d", "suf_toric_2d", "duf_toric_2d",
                    "sbuf_toric_2d", "dbuf_toric_2d"])
plot_compare2(["MWPM", "SUF", "DUF", "SBUF", "DBUF"], names, "l", [
    0.098], l, "weight", dim=2, yname=r"$ |\mathcal{C}|- |\mathcal{C}_{MWPM}| $", normy=0.1, output="mwcomp_uf_toric_2d_p98_norm")

# 2D planar comp weight uf
names = get_csvdir(["mwpm_planar_2d", "suf_planar_2d", "duf_planar_2d",
                    "sbuf_planar_2d", "dbuf_planar_2d"])
plot_compare2(["MWPM", "SUF", "DUF", "SBUF", "DBUF"], names, "l", [
    0.098], l, "weight", dim=2, yname=r"$ |\mathcal{C}|- |\mathcal{C}_{MWPM}| $", normy=0.1, output="mwcomp_uf_planar_2d_p98_norm")


l = [8+i*4 for i in range(4)]
# 3D planar comp weight uf
names = get_csvdir(["mwpm_toric_3d", "suf_toric_3d", "duf_toric_3d",
                    "sbuf_toric_3d", "dbuf_toric_3d"])
plot_compare2(["MWPM", "SUF", "DUF", "SBUF", "DBUF"], names, "l", [
    0.027], l, "weight", dim=3, yname=r"$ |\mathcal{C}|- |\mathcal{C}_{MWPM}| $", output="mwcomp_uf_toric_3d_p27_norm")

# 3D planar comp weight uf
names = get_csvdir(["mwpm_planar_3d", "suf_planar_3d", "duf_planar_3d",
                    "sbuf_planar_3d", "dbuf_planar_3d"])
plot_compare2(["MWPM", "SUF", "DUF", "SBUF", "DBUF"], names, "l", [
    0.027], l, "weight", dim=3, yname=r"$ |\mathcal{C}|- |\mathcal{C}_{MWPM}| $", output="mwcomp_uf_planar_3d_p27_norm")

