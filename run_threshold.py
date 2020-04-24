'''
2020 Mark Shui Hu, QuTech

www.github.com/watermarkhu/oop_surface_code
_____________________________________________

'''
from oopsc.threshold import sim_thresholds
import argparse
from run_oopsc import add_args


parser = argparse.ArgumentParser(
    prog="threshold_run",
    description="run a threshold computation",
    usage='%(prog)s [-h/--help] decoder lattice_type iters -l [..] -p [..] (lattice_size)'
)

parser.add_argument("decoder",
    action="store",
    type=str,
    help="type of decoder - {mwpm/uf/ufbb}",
    metavar="d",
)

parser.add_argument("lattice_type",
    action="store",
    type=str,
    help="type of lattice - {toric/planar}",
    metavar="lt",
)

parser.add_argument("iters",
    action="store",
    type=int,
    help="number of iterations - int",
    metavar="i",
)

key_arguments = [
    ["-l", "--lattices", "store", "lattice sizes - verbose list int", dict(type=int, nargs='*', metavar="", required=True)],
    ["-p", "--perror", "store", "error rates - verbose list float", dict(type=float, nargs='*', metavar="", required=True)],
    ["-me", "--measurement_error", "store_true", "enable measurement error (2+1D) - toggle", dict()],
    ["-mt", "--multithreading", "store_true", "use multithreading - toggle", dict()],
    ["-nt", "--threads", "store", "number of threads", dict(type=int, metavar="")],
    ["-ma", "--modified_ansatz", "store_true", "use modified ansatz - toggle", dict()],
    ["-s", "--save_result", "store_true", "save results - toggle", dict()],
    ["-sp", "--show_plot", "store_true", "show plot - toggle", dict()],
    ["-fn", "--file_name", "store", "plot filename - toggle", dict(default="thres", metavar="")],
    ["-pt", "--plot_title", "store", "plot filename - toggle", dict(default="", metavar="")],
    ["-f", "--folder", "store", "base folder path - toggle", dict(default="./", metavar="")],
    ["-sf", "--subfolder", "store_true", "store figures and data in subfolders - toggle", dict()],
    ["-pb", "--progressbar", "store_true", "enable progressbar - toggle", dict()],
    ["-dgc", "--dg_connections", "store_true", "use dg_connections pre-union processing - toggle", dict()],
    ["-dg", "--directed_graph", "store_true", "use directed graph for evengrow - toggle", dict()],
    ["-db", "--debug", "store_true", "enable debugging hearistics - toggle", dict()],
]

add_args(parser, key_arguments)
args=vars(parser.parse_args())
decoder = args.pop("decoder")


if decoder == "mwpm":
    from oopsc.decoder import mwpm as decode
    print(f"{'_'*75}\n\ndecoder type: minimum weight perfect matching (blossom5)")
elif decoder == "uf":
    from oopsc.decoder import uf as decode
    print(f"{'_'*75}\n\ndecoder type: unionfind")
    if args["dg_connections"]:
        print(f"{'_'*75}\n\nusing dg_connections pre-union processing")
elif decoder == "ufbb":
    from oopsc.decoder import ufbb as decode
    print("{}\n\ndecoder type: unionfind balanced bloom with {} graph".format("_"*75,"directed" if args["directed_graph"] else "undirected"))
    if args["dg_connections"]:
        print(f"{'_'*75}\n\nusing dg_connections pre-union processing")

sim_thresholds(decode, **args)
