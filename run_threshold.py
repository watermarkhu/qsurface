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
    ["decoder", "store", str, "type of decoder - {mwpm/uf_uwg/uf/ufbb}", "d", dict()],
    ["lattice_type", "store", str, "type of lattice - {toric/planar}", "lt", dict()],
    ["iters", "store", int, "number of iterations - int", "i", dict()]
]

key_arguments = [
    ["-l", "--lattices", "store", "lattice sizes - verbose list int", dict(type=int, nargs='*', metavar="", required=True)],
    ["-p", "--perror", "store", "error rates - verbose list float", dict(type=str, nargs='*', metavar="", required=True)],
    ["-me", "--measurement_error", "store_true", "enable measurement error (2+1D) - toggle", dict()],
    ["-mt", "--multithreading", "store_true", "use multithreading - toggle", dict()],
    ["-nt", "--threads", "store", "number of threads", dict(type=int, metavar="")],
    ["-o", "--output", "store", "output file name (no path, ext)", dict(default="", metavar="")],
    ["-f", "--folder", "store", "base folder path", dict(default=".", metavar="")],
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

decoders = __import__("simulator.decoder", fromlist=[decoder])
decode = getattr(decoders, decoder)

decoder_names = {
    "mwpm":     "minimum weight perfect matching (blossom5)",
    "uf":       "union-find",
    "uf_uwg":   "union-find non weighted growth",
    "ufbb":     "union-find balanced bloom"
}
decoder_name = decoder_names[decoder] if decoder in decoder_names else decoder
print(f"{'_'*75}\n\ndecoder type: " + decoder_name)

sim_thresholds(decode, **args)
