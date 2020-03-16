'''
2020 Mark Shui Hu, QuTech

www.github.com/watermarkhu/oop_surface_code
_____________________________________________

Contains methods to run a simulated lattice of the surface code.
The graph type (2D/3D) and decoder (MWPM, unionfind...) are specified and are loaded.
One can choose to run a simulated lattice for a single, multiple or many (multithreaded) multiple iterations.

'''
from progiter import ProgIter
import multiprocessing as mp
from decorators import debug as db
from decimal import Decimal as decimal
from collections import defaultdict as dd
from pprint import pprint
import printing as pr
import numpy as np
import random
import time


def init_random_seed(timestamp=None, worker=0, iteration=0, **kwargs):
    '''
    Initializes a random seed based on the current time, simulaton worker and iteration, which ensures a unique seed
    '''
    if timestamp is None:
        timestamp = time.time()
    seed = "{:.0f}".format(timestamp*10**7) + str(worker) + str(iteration)
    random.seed(decimal(seed))
    # print(seed)
    return seed


def apply_random_seed(seed=None, **kwargs):
    '''
    Applies a certain seed in the same format as init_random_seed()
    '''
    if seed is None:
        seed = init_random_seed()
    if type(seed) is not decimal:
        seed = decimal(seed)
    random.seed(seed)


def lattice_type(type, config, dec, go, size, **kwargs):
    '''
    Initilizes the graph and decoder type based on the lattice structure.
    '''
    if type == "toric":
        decoder = dec.toric(**config, plot_config=config, **kwargs)
        graph = go.toric(size, decoder, **config, plot_config=config, **kwargs)
    elif type == "planar":
        decoder = dec.planar(**config, plot_config=config, **kwargs)
        graph = go.planar(size, decoder, **config, plot_config=config, **kwargs)
    return graph


def get_mean_var(list_of_var, str):
    if list_of_var:
        return {
            str+"_m": np.mean(list_of_var),
            str+"_v": np.std(list_of_var)
        }
    else:
        return {str+"_m": 0, str+"_v": 0}


def single(
    size,
    config,
    ltype="toric",
    paulix=0,
    pauliz=0,
    erasure=0,
    measurex=0,
    measurez=0,
    dec=None,
    go=None,
    graph=None,
    worker=0,
    iter=0,
    seed=None,
    called=True,
    debug=False,
    **kwargs
):
    """
    Runs the peeling decoder for one iteration
    """
    # Initialize lattice
    if graph is None:
        pr.print_configuration(config, 1, size=size, pX=paulix, pZ=pauliz, pE=erasure, pmX=measurex, pmZ=measurez)
        graph = lattice_type(ltype, config, dec, go, size, **kwargs)

    # Initialize errors
    if seed is None and not config["seeds"]:
        init_random_seed(worker=worker, iteration=iter)
    elif seed is not None:
        apply_random_seed(seed)
    elif config["seeds"]:
        apply_random_seed(config["seeds"][0])

    graph.apply_and_measure_errors(pX=paulix, pZ=pauliz, pE=erasure, pmX=measurex, pmZ=measurez)

    # Peeling decoder
    graph.decoder.decode()

    # Measure logical operator
    graph.count_matching_weight()
    logical_error, correct = graph.logical_error()
    graph.reset()

    if called:
        output = dict(
            N       = 1,
            succes  = correct,
        )
        if debug:
            output.update(dict(
                weight  = graph.matching_weight[0],
                time    = graph.decoder.time,
                gbu     = graph.decoder.gbu,
                gbo     = graph.decoder.gbo,
                ufu     = graph.decoder.ufu,
                uff     = graph.decoder.uff,
                ctd     = graph.decoder.ctd,
                mac     = graph.decoder.mac,
            ))
    else:
        output = correct

    return output


def multiple(
    size,
    config,
    iters,
    ltype="toric",
    paulix=0,
    pauliz=0,
    erasure=0,
    measurex=0,
    measurez=0,
    dec=None,
    go=None,
    graph=None,
    qres=None,
    worker=0,
    seeds=None,
    called=True,
    progressbar=True,
    debug=False,
    **kwargs
):
    """
    Runs the peeling decoder for a number of iterations. The graph is reused for speedup.
    """

    if qres is None:
        pr.print_configuration(config, iters, size=size, paulix=paulix, pauliz=pauliz, erasure=erasure, measurex=measurex, measurez=measurez)
    if graph is None:
        graph = lattice_type(ltype, config, dec, go, size, **kwargs)

    if seeds is None and not config["seeds"]:
        seeds = [init_random_seed(worker=worker, iteration=iter) for iter in range(iters)]
    elif not config["seeds"]:
        seeds = config["seeds"]

    options = dict(
        ltype=ltype,
        paulix=paulix,
        pauliz=pauliz,
        erasure=erasure,
        measurex=measurex,
        measurez=measurez,
        graph=graph,
        worker=worker,
        called=0,
        debug=debug,
    )

    zipped = zip(ProgIter(range(iters)), seeds) if progressbar else zip(range(iters), seeds)
    result = [single(size, config, iter=iter, seed=seed, **options, **kwargs) for iter, seed in zipped]

    if called:
        output = dict(
            N       = iters,
            succes  = sum(result)
        )
        if debug:
            output.update(**get_mean_var(graph.matching_weight, "weight"))
            for key, value in graph.decoder.clist.items():
                output.update(**get_mean_var(value, key))
            db.reset_counters(graph)
        return output
    else:
        output = dict(
            N         = iters,
            succes    = sum(result),
        )
        if debug:
            output.update(weight = graph.matching_weight)
            output.update(**graph.decoder.clist)
            db.reset_counters(graph)
        qres.put(output)


def multiprocess(
        size,
        config,
        iters,
        dec=None,
        go=None,
        graph=None,
        processes=None,
        node=0,
        debug=False,
        **kwargs
    ):
    """
    Runs the peeling decoder for a number of iterations, split over a number of processes
    """
    pr.print_configuration(config, iters, **kwargs)

    if processes is None:
        processes = mp.cpu_count()

    # Calculate iterations for ieach child process
    process_iters = iters // processes

    # Initiate processes
    qres = mp.Queue()
    workers = []

    options = dict(
        dec=dec,
        go=go,
        qres=qres,
        called=0,
        debug=debug
    )

    if graph is None or len(graph) != processes:
        graph = [None]*processes

    for i, g in enumerate(graph, int(node*processes)):
        workers.append(
            mp.Process(
                target=multiple,
                args=(size, config, process_iters),
                kwargs=dict(worker=i, graph=g, **options, **kwargs),
            )
        )
    print("Starting", processes, "workers.")

    # Start and join processes
    for worker in workers:
        worker.start()

    workerlists, output = dd(list), dd(int)
    for worker in workers:
        for key, value in qres.get().items():
            if type(value) == list:
                workerlists[key].extend(value)
            else:
                output[key] += value

    # from guppy import hpy
    # h = hpy().heap()
    # print("\nmememory (MB):", h.size/1000000)

    for key, value in workerlists.items():
        output.update(get_mean_var(value, key))

    for worker in workers:
        worker.join()

    return output


def default_config(**kwargs):
    '''
    stores all settings of the decoder
    '''
    config = dict(

        seeds          = [],
        plot2D         = 0,
        plot3D         = 0,
        plotUF         = 0,
        dg_connections = 0,
        directed_graph = 0,
        print_steps    = 0,
        plot_find      = 0,
        plot_bucket    = 0,
        plot_cluster   = 0,
        plot_cut       = 0,
        plot_peel      = 0,
        plot_node      = 0,
        plot_size      = 6,
        linewidth      = 1.5,
        scatter_size   = 30,
        z_distance     = 8,
    )

    for key, value in kwargs.items():
        if key in kwargs:
            kwargs[key] = value

    return config


def add_args(parser, args):
    for name, action, type, help, metavar in args:
        parser.add_argument(name, action=action, type=type, help=help, metavar=metavar)


def add_kwargs(parser, args, group_name=None, description=None):

    if group_name:
        parser = parser.add_argument_group(group_name, description)
    for sid, lid, action, help, kwargs in args:
        parser.add_argument(sid, lid, action=action, help=help, **kwargs)


if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(
        prog="OOPSC",
        description="simulation of surface code using mwpm/uf/eg decoder",
        usage='%(prog)s [-h/--help] L (lattice_size)'
    )

    parser.add_argument("lattice_size",
        action="store",
        type=int,
        help="size of the lattce",
        metavar="L",
    )

    sim_arguments = [
        ["-i", "--iters", "store", "number of iterations - int", dict(type=int, default=1, metavar="")],
        ["-l", "--lattice_type", "store", "type of lattice - {toric/planar}", dict(type=str, choices=["toric", "planar"], default="toric", metavar="")],
        ["-d", "--decoder", "store", "type of decoder - {mwpm/uf/eg}", dict(type=str, choices=["mwpm", "uf", "eg"], default="eg", metavar="")],
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
        ["-dgc", "--dg_connections", "store_true", "use dg_connections pre-union processing - toggle", dict()],
        ["-dg", "--directed_graph", "store_true", "use directed graph for evengrow - toggle", dict()],
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
        import mwpm as decode
        print(f"{'_'*75}\n\ndecoder type: minimum weight perfect matching (blossom5)")
    elif decoder == "uf":
        import unionfind as decode
        print(f"{'_'*75}\n\ndecoder type: unionfind")
        if args["dg_connections"]:
            print(f"{'_'*75}\n\nusing dg_connections pre-union processing")
    elif decoder == "eg":
        import unionfind_eg as decode
        print("{}\n\ndecoder type: unionfind evengrow with {} graph".format("_"*75,"directed" if args["directed_graph"] else "undirected"))
        if args["dg_connections"]:
            print(f"{'_'*75}\n\nusing dg_connections pre-union processing")


    if (not f3d and config["measurex"] == 0 and config["measurez"] == 0) or f2d:
        import graph_2D as go
        print(f"{'_'*75}\n\ngraph type: 2D {config['ltype']}\n{'_'*75}\n")
    else:
        import graph_3D as go
        print(f"{'_'*75}\n\ngraph type: 3D {config['ltype']}\n{'_'*75}\n")


    if iters == 1:
        output = single(size, args, dec=decode, go=go, debug=debug, **config)
    elif not multi:
        output = multiple(size, args, iters, dec=decode, go=go, debug=debug, **config)
    else:
        output = multiprocess(size, args, iters, dec=decode, go=go, debug=debug, processes=threads, **config)

    pprint(output)
