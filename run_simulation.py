'''
2020 Mark Shui Hu

www.github.com/watermarkhu/OpenSurfaceSim
_____________________________________________

'''
import argparse
from pprint import pprint
from simulator.main import single, multiple, multiprocess


def add_args(parser, args):
    for name, action, type, help, metavar, kwargs in args:
        parser.add_argument(name, action=action, type=type, help=help, metavar=metavar, **kwargs)


def add_kwargs(parser, args, group_name=None, description=None):

    if group_name:
        parser = parser.add_argument_group(group_name, description)
    for sid, lid, action, help, kwargs in args:
        parser.add_argument(sid, lid, action=action, help=help, **kwargs)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="Surface code simulation",
        description="simulation of surface code using mwpm/uf/eg decoder",
        usage='%(prog)s [-h/--help] L (lattice_size)'
    )

    arguments = [["lattice_size", "store", int, "size of the lattce", "L", dict()]]

    sim_arguments = [
        ["-i", "--iters", "store", "number of iterations - int", dict(type=int, default=1, metavar="")],
        ["-l", "--lattice_type", "store", "type of lattice - {toric/planar}", dict(type=str, choices=["toric", "planar"], default="toric", metavar="")],
        ["-d", "--decoder", "store", "type of decoder - {mwpm/uf_uwg/uf/ufbb}", dict(type=str, default="ufbb", metavar="")],
        ["-px", "--paulix", "store", "Pauli X error rate - float {0,1}", dict(type=float, default=0, metavar="")],
        ["-pz", "--pauliz", "store", "Pauli Y error rate - float {0,1}", dict(type=float, default=0, metavar="")],
        ["-pmx", "--measurex", "store", "Measurement X error rate - float {0,1}", dict(type=float, default=0, metavar="")],
        ["-pmz", "--measurez", "store", "Measurement Y error rate - float {0,1}", dict(type=float, default=0, metavar="")],
        ["-pe", "--erasure", "store", "Erasure - float {0,1}", dict(type=float, default=0, metavar="")],
        ["-s", "--seeds", "store", "seeds for the simulations - verbose list", dict(type=int, nargs='*', metavar="")],
        ["-mt", "--multithreading", "store_true", "use multithreading - toggle", dict()],
        ["-nt", "--threads", "store", "number of threads (defaults to available # logical cores) - int", dict(type=int, metavar="")],
        ["-f2d", "--force2D", "store_true", "force 2D lattice - toggle", dict()],
        ["-f3d", "--force3D", "store_true", "force 3D lattice - toggle", dict()],
    ]

    decoder_arguments = [
        ["-fb", "--fbloom", "store", "pdc minimization paramter fbloom - float {0,1}",  dict(type=float, default=0.5, metavar="")],
        ["-dgc", "--dg_connections", "store_true", "use dg_connections pre-union processing - toggle", dict()],
        ["-dg", "--directed_graph", "store_true", "use directed graph for balanced bloom - toggle", dict()],
        ["-db", "--debug", "store_true", "enable debugging hearistics - toggle", dict()]
    ]

    plot_arguments = [
        ["-pr", "--print_steps", "store_true", "print all debug info - toggle", dict()],
        ["-p2d", "--plot2D", "store_true", "plot 2D lattice - toggle", dict()],
        ["-p3d", "--plot3D", "store_true", "plot 3D lattice - toggle", dict()],
        ["-puf", "--plotUF", "store_true", "plot uf-lattice - toggle", dict()],
        ["-pf", "--plot_find", "store_true", "plot find cluster routine sequenctially - toggle", dict()],
        ["-pb", "--plot_bucket", "store_true", "plot growth routine by bucket - toggle", dict()],
        ["-pc", "--plot_cluster", "store_true", "plot growth routine by cluster - toggle", dict()],
        ["-pn", "--plot_node", "store_true", "plot growth routine by node - toggle", dict()],
        ["-pk", "--plot_cut", "store_true", "plot removed edges of cluster cycles - toggle", dict()],
        ["-pp", "--plot_peel", "store_true", "plot the peeling of edges sequentially - toggle", dict()],
    ]

    add_args(parser, arguments)
    add_kwargs(parser, sim_arguments, "simulation", "arguments for simulation")
    add_kwargs(parser, decoder_arguments, "decoder", "arguments for decoder")
    add_kwargs(parser, plot_arguments, "figure", "arguments for plotting")


    config=vars(parser.parse_args())
    decoder = config.pop("decoder")
    iters   = config.pop("iters")
    multi   = config.pop("multithreading")
    threads = config.pop("threads")
    size    = config.pop("lattice_size")
    debug   = config.pop("debug")
    f2d     = config.pop("force2D")
    f3d     = config.pop("force3D")

    kwargs = dict(
        ltype   = config.pop("lattice_type"),
        paulix      = config.pop("paulix"),
        pauliz      = config.pop("pauliz"),
        erasure      = config.pop("erasure"),
        measurex     = config.pop("measurex"),
        measurez     = config.pop("measurez"),
    )

    print(f"{'_'*75}\n")
    print(f"OpenSurfaceSim\n2020 Mark Shui Hu\nwww.github.com/watermarkhu/OpenSurfaceSim")

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


    if (not f3d and kwargs["measurex"] == 0 and kwargs["measurez"] == 0) or f2d:
        from simulator.graph import graph_2D as go
        print(f"{'_'*75}\n\ngraph type: 2D {kwargs['ltype']}\n{'_'*75}\n")
    else:
        from simulator.graph import graph_3D as go
        print(f"{'_'*75}\n\ngraph type: 3D {kwargs['ltype']}\n{'_'*75}\n")


    if iters == 1:
        output = single(size, config, dec=decode, go=go, debug=debug, **kwargs)
    elif not multi:
        output = multiple(size, config, iters, dec=decode, go=go, debug=debug, **kwargs)
    else:
        output = multiprocess(size, config, iters, dec=decode, go=go, debug=debug, processes=threads, **kwargs)

    # pprint(output)
