'''
2020 Mark Shui Hu, QuTech

www.github.com/watermarkhu/oop_surface_code
_____________________________________________

'''
import argparse
from run_oopsc import add_args
from oopsc.threshold import read_data, fit_thresholds

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
    ["-f", "--folder", "store", "base folder path - toggle", dict(default="./")],
    ["-ma", "--modified_ansatz", "store_true", "use modified ansatz - toggle", dict()],
    ["-ds", "--data_select", "store", "selective plot data - {even/odd}", dict(type=str, choices=["even", "odd"], metavar="")]
]

add_args(parser, key_arguments)
args=vars(parser.parse_args())

data = read_data(args.pop("folder") + args.pop("file_name"))
fit_thresholds(data, **args)
