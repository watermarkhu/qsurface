'''
2020 Mark Shui Hu

www.github.com/watermarkhu/OpenSurfaceSim
_____________________________________________

'''
import argparse
from run_simulation import add_args, add_kwargs
from opensurfacesim.threshold.plot import plot_thresholds


parser = argparse.ArgumentParser(
    prog="threshold_fit",
    description="fit a threshold computation",
    usage='%(prog)s [-h/--help] file_name'
)

arguments = [["file_name", "store", str, "file name of csv data (without extension)", "file_name", dict()]]

key_arguments = [
    ["-p", "--probs", "store", "p items to plot - verbose list", dict(type=float, nargs='*', metavar="")],
    ["-l", "--latts", "store", "L items to plot - verbose list", dict(type=float, nargs='*', metavar="")],
    ["-ma", "--modified_ansatz", "store_true", "use modified ansatz - toggle", dict()],
    ["-o", "--output", "store", "output file name", dict(type=str, default="", metavar="")],
    ["-pt", "--plot_title", "store", "plot filename", dict(type=str, default="", metavar="")],
    ["-ymin", "--ymin", "store", "limit yaxis min", dict(type=float, default=0.5, metavar="")],
    ["-ymax", "--ymax", "store", "limit yaxis max", dict(type=float, default=1, metavar="")],

]

add_args(parser, arguments)
add_kwargs(parser, key_arguments)
args=vars(parser.parse_args())
plot_thresholds(**args)
