import run_surface_code as run
import unionfind as decoder

size = 10

pX = 0.05
pZ = 0.0
pE = 0.05
iters = 50000

class decoder_config(object):
    def __init__(self, path="./unionfind.ini"):

        self.plot_load = 1
        self.seed = None
        self.type = "planar"

        self.decoder = {
            "print_steps": 1,
            "random_order": False,
            "random_traverse": False,
            "plot_find"     : 0,
            "plot_growth"   : 0,
            "plot_peel"     : 0,

            # Tree-method
            "intervention": False,
            "vcomb": False,

            # Evengrow
            "plot_nodes": 1,
            "print_nodetree": 1,
        }

        self.file = {
            "savefile": 0,
            "erasure_file": None,
            "pauli_file": None,
        }

        self.plot = {
            "plot_size"     : 6,
            "line_width"    : 1.5,
            "plotstep_click": 1,
        }


output = run.single(size, decoder_config(), decoder, pE, pX, pZ, dec=decoder, config=decoder_config())
# output = run.multiple(size, iters, pE, pX, pZ, dec=decoder, config=decoder_config())
# output = run.multiprocess(size, iters, pE, pX, pZ, dec=decoder, config=decoder_config())
