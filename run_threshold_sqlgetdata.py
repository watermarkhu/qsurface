'''
2020 Mark Shui Hu, QuTech

www.github.com/watermarkhu/oop_surface_code
_____________________________________________

'''
import argparse
from run_oopsc import add_kwargs
from oopsc.batch.sql import get_data


parser = argparse.ArgumentParser(
    prog="mysql datagetter",
    description="saves a mysql database",
)

kwargs = [
    ["-d", "--database", "store", "name of database", dict(type=str, metavar="")],
    ["-f", "--folder", "store", "folder of csv files", dict(type=str, metavar="")],
    ["-o", "--output", "store", "output, needs to add file ex.", dict(type=str, metavar="")],
]

add_kwargs(parser, kwargs)

args=vars(parser.parse_args())
get_data(**args)
