'''
2020 Mark Shui Hu, QuTech

www.github.com/watermarkhu/oop_surface_code
_____________________________________________

'''
import argparse
from run_oopsc import add_args
from oopsc.threshold import read_data, plot_thresholds


parser = argparse.ArgumentParser(
    prog="threshold_fit",
    description="fit a threshold computation",
    usage='%(prog)s [-h/--help] file_name'
)

parser.add_argument("file_name",
    action="store",
    type=str,
    help="file name of csv data (without extension)",
    metavar="file_name",
)

key_arguments = [
    ["-ds", "--data_select", "store", "selective plot data - {even/odd}", dict(type=str, choices=["even", "odd"], metavar="")],
    ["-ma", "--modified_ansatz", "store_true", "use modified ansatz - toggle", dict()],
    ["-s", "--save_result", "store_true", "save results - toggle", dict()],
    ["-pt", "--plot_title", "store", "plot filename - toggle", dict(default="")],
    ["-f", "--folder", "store", "base folder path - toggle", dict(default="./")],
]

add_args(parser, key_arguments)
args=vars(parser.parse_args())

folder = args.pop("folder")
name = args.pop("file_name")
data = read_data(folder + name)
fig_path = folder + "figures/" + name + ".pdf"
plot_thresholds(data, **args)
