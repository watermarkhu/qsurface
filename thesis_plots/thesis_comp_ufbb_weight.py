
from compare_heuristics import plot_compare, plot_compare2, latex_style, get_csvdir


l = [8+i*8 for i in range(8)]
output=None
latex_style(scale=0.5, y=1)


output = "mwcomp_ufbb_toric_2d_p98_norm"
names = get_csvdir(["mwpm_toric_2d", "ufbb_toric_2d", "dbuf_toric_2d"])
plot_compare2(["MWPM", "UFBB", "DBUF"], names, "l", [
    0.1], l, "weight", dim=2, yname=r"$ |\mathcal{C}|/ |\mathcal{C}_{MWPM}| $", normy=0.1, output=output)

# 2D planar comp weight uf
output = "mwcomp_ufbb_planar_2d_p98_norm"
names = get_csvdir(["mwpm_planar_2d", "ufbb_planar_2d", "dbuf_planar_2d"])
plot_compare2(["MWPM", "UFBB", "DBUF"], names, "l", [
    0.1], l, "weight", dim=2, yname=r"$ |\mathcal{C}|/ |\mathcal{C}_{MWPM}| $", normy=0.1, output=output)


l = [8+i*4 for i in range(4)]
# 3D planar comp weight uf
output = "mwcomp_ufbb_toric_3d_p27_norm"
names = get_csvdir(["mwpm_toric_3d", "ufbb_toric_3d", "dbuf_toric_3d"])
plot_compare2(["MWPM", "UFBB", "DBUF"], names, "l", [
    0.027], l, "weight", dim=3, yname=r"$ |\mathcal{C}|/ |\mathcal{C}_{MWPM}| $", output=output)

# 3D planar comp weight uf
output = "mwcomp_ufbb_planar_3d_p27_norm"
names = get_csvdir(["mwpm_planar_3d", "ufbb_planar_3d", "dbuf_planar_3d"])
plot_compare2(["MWPM", "UFBB", "DBUF"], names, "l", [
    0.027], l, "weight", dim=3, yname=r"$ |\mathcal{C}|/ |\mathcal{C}_{MWPM}| $", output=output)

