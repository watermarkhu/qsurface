from matplotlib_latexstyle import *
import sys
sys.path.insert(0, '..')

from oopsc.threshold.sim import read_data
from oopsc.threshold.plot import plot_thresholds

data1 = "../cartesiusdata/mwpm_toric_2d.csv"
data2 = "../cartesiusdata/mwpm_planar_2d.csv"

f0, f1 = plot_thresholds(data1, show_plot=False)
f0, f1 = plot_thresholds(data2, f0=f0, f1=f1, styles=["x", "--"],show_plot=False)

f0.tight_layout()

plt.show(f0)