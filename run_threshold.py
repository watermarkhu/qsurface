'''
2020 Mark Shui Hu

www.github.com/watermarkhu/OpenSurfaceSim
_____________________________________________

'''
import argparse
from run_simulation import add_args, add_kwargs
from simulator.threshold.sim import sim_thresholds


parser = argparse.ArgumentParser(
    prog="Threshold simulations",
    description="run a threshold computation",
    usage='%(prog)s [-h/--help] decoder lattice_type iters -l [..] -p [..] (lattice_size)'
)

arguments = [
    ["code", "store", str, "type of surface code", "c", dict()],
    ["decode_module", "store", str, "type of decoder", "d", dict()],
    ["iters", "store", int, "number of iterations - int", "i", dict()]
]

key_arguments = [
    ["-l", "--lattices", "store", "lattice sizes - verbose list int", dict(type=int, nargs='*', metavar="", required=True)],
    ["-p", "--perror", "store", "error rates - verbose list float", dict(type=str, nargs='*', metavar="", required=True)],
    ["-pm", "--perfect_measurements", "store_true", "force perfect measurements (2D)", dict()],
    ["-mt", "--multithreading", "store_true", "use multithreading - toggle", dict()],
    ["-nt", "--threads", "store", "number of threads", dict(type=int, metavar="")],
    ["-o", "--output", "store", "output file name (no path, ext)", dict(default="", metavar="")],
    ["-f", "--folder", "store", "base folder path", dict(default=".", metavar="")],
    ["-pb", "--progressbar", "store_true", "enable progressbar - toggle", dict()],
    ["-bm", "--benchmark", "store_true", "enable statistics - toggle", dict()]
]

add_args(parser, arguments)
add_kwargs(parser, key_arguments)
args=vars(parser.parse_args())
sim_thresholds(**args)
