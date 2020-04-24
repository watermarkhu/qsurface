'''
2020 Mark Shui Hu, QuTech

www.github.com/watermarkhu/oop_surface_code
_____________________________________________

'''
import argparse
from pprint import pprint
from oopsc.oopsc import single, multiple, multiprocess


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
        prog="OOPSC",
        description="simulation of surface code using mwpm/uf/eg decoder",
        usage='%(prog)s [-h/--help] L (lattice_size)'
    )

    arguments = [["lattice_size", "store", int, "size of the lattce", "L", dict()]]

    sim_arguments = [
        ["-i", "--iters", "store", "number of iterations - int", dict(type=int, default=1, metavar="")],
        ["-l", "--lattice_type", "store", "type of lattice - {toric/planar}", dict(type=str, choices=["toric", "planar"], default="toric", metavar="")],
        ["-d", "--decoder", "store", "type of decoder - {mwpm/uf/ufbb}", dict(type=str, choices=["mwpm", "uf", "ufbb"], default="ufbb", metavar="")],
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
        ["-p2d", "--plot2D", "store_true", "plot 2D lattice - toggle", dict()],
        ["-p3d", "--plot3D", "store_true", "plot 3D lattice - toggle", dict()],
        ["-puf", "--plotUF", "store_true", "plot uf-lattice - toggle", dict()],
        ["-pr", "--print_steps", "store_true", "print all debug info - toggle", dict()],
        ["-pf", "--plot_find", "store_true", "plot find cluster routine sequenctially - toggle", dict()],
        ["-pb", "--plot_bucket", "store_true", "plot growth routine by bucket - toggle", dict()],
        ["-pc", "--plot_cluster", "store_true", "plot growth routine by cluster - toggle", dict()],
        ["-pn", "--plot_node", "store_true", "plot growth routine by node - toggle", dict()],
        ["-pk", "--plot_cut", "store_true", "plot removed edges of cluster cycles - toggle", dict()],
        ["-pp", "--plot_peel", "store_true", "plot the peeling of edges sequentially - toggle", dict()],
        ["-ps", "--plot_size", "store", "size of plotting window - int", dict(type=int, default=6, metavar="")],
        ["-lw", "--linewidth", "store", "width of line plots - int/float", dict(type=float, default=1.5, metavar="")],
        ["-ss", "--scatter_size", "store", "size of 3D plot scatter - int/float", dict(type=int, default=30, metavar="")],
        ["-zd", "--z_distance", "store", "distance between z layers in 3D plot - int/float", dict(type=int, default=2, metavar="")],
    ]

    add_args(parser, arguments)
    add_kwargs(parser, sim_arguments, "simulation", "arguments for simulation")
    add_kwargs(parser, decoder_arguments, "decoder", "arguments for decoder")
    add_kwargs(parser, plot_arguments, "figure", "arguments for plotting")


    args=vars(parser.parse_args())
    decoder = args.pop("decoder")
    iters   = args.pop("iters")
    multi   = args.pop("multithreading")
    threads = args.pop("threads")
    size    = args.pop("lattice_size")
    debug   = args.pop("debug")
    f2d     = args.pop("force2D")
    f3d     = args.pop("force3D")

    config = dict(
        ltype   = args.pop("lattice_type"),
        paulix      = args.pop("paulix"),
        pauliz      = args.pop("pauliz"),
        erasure      = args.pop("erasure"),
        measurex     = args.pop("measurex"),
        measurez     = args.pop("measurez"),
    )

    print(f"{'_'*75}\n")
    print(f"OOP surface code simulations\n2020 Mark Shui Hu, QuTech\nwww.github.com/watermarkhu/oop_surface_code")

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


    if (not f3d and config["measurex"] == 0 and config["measurez"] == 0) or f2d:
        from oopsc.graph import graph_2D as go
        print(f"{'_'*75}\n\ngraph type: 2D {config['ltype']}\n{'_'*75}\n")
    else:
        from oopsc.graph import graph_3D as go
        print(f"{'_'*75}\n\ngraph type: 3D {config['ltype']}\n{'_'*75}\n")


    if iters == 1:
        output = single(size, args, dec=decode, go=go, debug=debug, **config)
    elif not multi:
        output = multiple(size, args, iters, dec=decode, go=go, debug=debug, **config)
    else:
        output = multiprocess(size, args, iters, dec=decode, go=go, debug=debug, processes=threads, **config)

    pprint(output)
