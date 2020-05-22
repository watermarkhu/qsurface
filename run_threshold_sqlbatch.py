'''
2020 Mark Shui Hu, QuTech

www.github.com/watermarkhu/oop_surface_code
_____________________________________________

'''

import argparse
from run_oopsc import add_args, add_kwargs
from oopsc.batch.sim import sim_thresholds

parser = argparse.ArgumentParser(
    prog="threshold_run",
    description="run a threshold computation",
    usage='%(prog)s [-h/--help] decoder lattice_type iters -l [..] -p [..] (lattice_size)'
)

args = [
    ["node", "store", int, "node number", "node", dict()],
    ["processes", "store", int, "number of processes", "processes", dict()],
    ["decoder", "store", str, "type of decoder - {mwpm/uf_uwg/uf/ufbb}", "d", dict()],
    ["lattice_type", "store", str, "type of lattice - {toric/planar}", "lt", dict()],
    ["iters", "store", int, "number of iterations - int", "i", dict()],
]

pos_arguments= [
    ["-l", "--lattices", "store", "lattice sizes - verbose list int", dict(type=int, nargs='*', metavar="", required=True)],
    ["-p", "--perror", "store", "error rates - verbose list float", dict(type=float, nargs='*', metavar="", required=True)],
]

key_arguments = [
    ["-sql", "--database", "store", "sql database name", dict(type=str, default="", metavar="")],
    ["-of", "--outputfolder", "store", "output folder", dict(type=str, default="", metavar="")],
    ["-me", "--measurement_error", "store_true", "enable measurement error (2+1D) - toggle", dict()],
    ["-pb", "--progressbar", "store_true", "enable progressbar - toggle", dict()],
    ["-dgc", "--dg_connections", "store_true", "use dg_connections pre-union processing - toggle", dict()],
    ["-dg", "--directed_graph", "store_true", "use directed graph for balanced bloom - toggle", dict()],
    ["-db", "--debug", "store_true", "enable debugging hearistics - toggle", dict()],
]

add_args(parser, args)
add_kwargs(parser, pos_arguments, "positional", "range of L and p values")
add_kwargs(parser, key_arguments)

args=vars(parser.parse_args())
decoder = args.pop("decoder")

decoders = __import__("oopsc.decoder", fromlist=[decoder])
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
