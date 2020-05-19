'''
2020 Mark Shui Hu, QuTech

www.github.com/watermarkhu/oop_surface_code
_____________________________________________

'''
import argparse
from run_oopsc import add_args, add_kwargs
from oopsc.threshold.sim import sim_thresholds


parser = argparse.ArgumentParser(
    prog="threshold_run",
    description="run a threshold computation",
    usage='%(prog)s [-h/--help] decoder lattice_type iters -l [..] -p [..] (lattice_size)'
)

arguments = [
    ["decoder", "store", str, "type of decoder - {mwpm/uf_uwg/uf/ufbb}", "d", dict(choices=["mwpm", "uf_uwg", "uf", "ufbb"])],
    ["lattice_type", "store", str, "type of lattice - {toric/planar}", "lt", dict()],
    ["iters", "store", int, "number of iterations - int", "i", dict()]
]

key_arguments = [
    ["-l", "--lattices", "store", "lattice sizes - verbose list int", dict(type=int, nargs='*', metavar="", required=True)],
    ["-p", "--perror", "store", "error rates - verbose list float", dict(type=float, nargs='*', metavar="", required=True)],
    ["-me", "--measurement_error", "store_true", "enable measurement error (2+1D) - toggle", dict()],
    ["-mt", "--multithreading", "store_true", "use multithreading - toggle", dict()],
    ["-nt", "--threads", "store", "number of threads", dict(type=int, metavar="")],
    ["-s", "--save_result", "store_true", "save results - toggle", dict()],
    ["-fn", "--file_name", "store", "plot filename - toggle", dict(default="thres", metavar="")],
    ["-f", "--folder", "store", "base folder path - toggle", dict(default="./", metavar="")],
    ["-pb", "--progressbar", "store_true", "enable progressbar - toggle", dict()],
    ["-fb", "--fbloom", "store", "pdc minimization parameter fbloom - float {0,1}",  dict(type=float, default=0.5, metavar="")],
    ["-dgc", "--dg_connections", "store_true", "use dg_connections pre-union processing - toggle", dict()],
    ["-dg", "--directed_graph", "store_true", "use directed graph for evengrow - toggle", dict()],
    ["-db", "--debug", "store_true", "enable debugging heuristics - toggle", dict()],
]

add_args(parser, arguments)
add_kwargs(parser, key_arguments)
args=vars(parser.parse_args())
decoder = args.pop("decoder")

if decoder == "mwpm":
    from oopsc.decoder import mwpm as decode
    print(f"{'_'*75}\n\ndecoder type: minimum weight perfect matching (blossom5)")
elif decoder[:2] == "uf":
    if decoder == "uf":
        from oopsc.decoder import uf as decode
        print(f"{'_'*75}\n\ndecoder type: unionfind")
    elif decoder == "ufbb":
        from oopsc.decoder import ufbb as decode
        print("{}\n\ndecoder type: unionfind balanced bloom with {} graph".format(
            "_"*75, "directed" if args["directed_graph"] else "undirected"))
    elif decoder == "uf_uwg":
        from oopsc.decoder import uf_uwg as decode
        print(f"{'_'*75}\n\ndecoder type: unionfind unweighted growth")

    if args["dg_connections"]:
        print(f"{'_'*75}\n\nusing dg_connections pre-union processing")

sim_thresholds(decode, **args)
