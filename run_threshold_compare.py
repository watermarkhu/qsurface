'''
2020 Mark Shui Hu

www.github.com/watermarkhu/oop_surface_code
_____________________________________________
'''

import argparse
from run_simulation import add_args, add_kwargs
from simulator.threshold.plot import plot_compare

parser = argparse.ArgumentParser(
    prog="threshold_compare",
    description="can compare thresholds and other parameters of different sims",
)

arguments = [
    ["feature", "store", str, "feature to plot", "feat", dict()],
    [ "xaxis", "store", str, "xaxis of comparison {l/p}", "xaxis", dict(choices=["l", "p"])]
]

key_arguments= [
    ["-n", "--csv_names", "store", "CSV databases to plot - verbose list str", dict(type=str, nargs='*', metavar="", required=True)],
    ["-p", "--probs", "store", "p items to plot - verbose list", dict(type=float, nargs='*', metavar="")],
    ["-l", "--latts", "store", "L items to plot - verbose list", dict(type=float, nargs='*', metavar="")],
    ["-e", "--plot_error", "store_true", "plot standard deviation - toggle", dict()],
    ["-a", "--average", "store_true", "average p - toggle", dict()],
    ["-f", "--fitname", "store", "fit class name", dict(type=str, default="", metavar="")],
    ["-d", "--dim", "store", "dimension", dict(type=int, default=1, metavar="")],
    ["-ms", "--ms", "store", "markersize", dict(type=int, default=5, metavar="")],
    ["-m", "--xm", "store", "x axis multiplier", dict(type=int, default=1, metavar="")],
    ["-o", "--output", "store", "output file name", dict(type=str, default="", metavar="")],
]

add_args(parser, arguments)
add_kwargs(parser, key_arguments)
args=vars(parser.parse_args())
plot_compare(**args)
