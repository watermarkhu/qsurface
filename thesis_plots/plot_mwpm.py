from matplotlib_latexstyle import *
import sys
sys.path.insert(0, '..')

from oopsc import threshold
data1 = threshold.read_data("../cartesiusdata/mwpm_toric_2d.csv")
data2 = threshold.read_data("../cartesiusdata/mwpm_planar_2d.csv")

f0, f1 = threshold.plot_thresholds(data1, save_result=False, show_plot=False)
f0, f1 = threshold.plot_thresholds(data2, f0=f0, f1=f1, styles=["x", "--"], save_result=False)

