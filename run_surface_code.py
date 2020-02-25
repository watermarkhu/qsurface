'''
2020 Mark Shui Hu, QuTech

www.github.com/watermarkhu/toric_code
_____________________________________________

Contains methods to run a simulated lattice of the surface code.
The graph type (2D/3D) and decoder (MWPM, unionfind...) are specified and are loaded.
One can choose to run a simulated lattice for a single, multiple or many (multithreaded) multiple iterations.

'''
from progiter import ProgIter
import multiprocessing as mp
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
    return decoder, graph


def get_mean_var(list_of_var, str):
    if list_of_var:
        return {
            str+"_m": np.mean(list_of_var),
            str+"_v": np.std(list_of_var)
        }
    else:
        return {str+"_m": 0, str+"_v": 0}


def single(
    config,
    dec,
    go,
    ltype="toric",
    size=10,
    pX=0,
    pZ=0,
    pE=0,
    pmX=0,
    pmZ=0,
    graph=None,
    worker=0,
    iter=0,
    seed=None,
    **kwargs
):
    """
    Runs the peeling decoder for one iteration
    """
    # Initialize lattice
    if graph is None:
        pr.print_configuration(config, 1, size=size, pX=pX, pZ=pZ, pE=pE, pmX=pmX, pmZ=pmZ)
        decoder, graph = lattice_type(ltype, config, dec, go, size, **kwargs)

    # Initialize errors
    if seed is None and not config["seeds"]:
        init_random_seed(worker=worker, iteration=iter)
    elif seed is not None:
        apply_random_seed(seed)
    elif not config["seeds"]:
        apply_random_seed(config["seed"][0])

    graph.apply_and_measure_errors(pX=pX, pZ=pZ, pE=pE, pmX=pmX, pmZ=pmZ)

    # Peeling decoder
    graph.decoder.decode()

    # Measure logical operator
    graph.count_matching_weight()
    logical_error, correct = graph.logical_error()
    graph.reset()

    return correct


def multiple(
    iters,
    config,
    dec,
    go,
    ltype="toric",
    size=10,
    pX=0,
    pZ=0,
    pE=0,
    pmX=0,
    pmZ=0,
    qres=None,
    worker=0,
    seeds=None,
    **kwargs
):
    """
    Runs the peeling decoder for a number of iterations. The graph is reused for speedup.
    """

    if qres is None:
        pr.print_configuration(config, iters, size=size, pX=pX, pZ=pZ, pE=pE, pmX=pmX, pmZ=pmZ)

    if seeds is None and not config["seeds"]:
        seeds = [init_random_seed(worker=worker, iteration=iter) for iter in range(iters)]
    elif not config["seeds"]:
        seeds = config["seeds"]

    decoder, graph = lattice_type(ltype, config, dec, go, size, **kwargs)

    result = [
        single(config, dec, go, ltype, size, pX, pZ, pE, pmX, pmZ ,graph, worker, iter, seed, **kwargs)
        for iter, seed in zip(ProgIter(range(iters)), seeds)
    ]

    if qres is not None:
        output = {
            "N"         : iters,
            "succes"    : sum(result),
            "weight"    : graph.matching_weight,
            "time"      : decoder.time,
            "gbu"       : decoder.gbu,
            "gbo"       : decoder.gbo,
            "ufu"       : decoder.ufu,
            "uff"       : decoder.uff,
            "ctd"       : decoder.ctd,
        #     "mac"       : decoder.mac,
        }
        qres.put(output)
    else:
        output = {
            "N"         : iters,
            "succes"    : sum(result),
            **get_mean_var(graph.matching_weight, "weight"),
            **get_mean_var(decoder.time, "time"),
            **get_mean_var(decoder.gbu, "gbu"),
            **get_mean_var(decoder.gbo, "gbo"),
            **get_mean_var(decoder.ufu, "ufu"),
            **get_mean_var(decoder.uff, "uff"),
            **get_mean_var(decoder.ctd, "ctd"),
            # **get_mean_var(decoder.mac, "mac")
        }
        return output


def multiprocess(
        iters,
        config,
        dec,
        go,
        seeds=None,
        processes=None,
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
    rest_iters = iters - process_iters * (processes - 1)

    # Generate seeds for simulations
    if seeds is None:
        num_seeds = [process_iters for _ in range(processes - 1)] + [rest_iters]
        seed_lists = [[init_random_seed(worker=worker, iteration=iter) for iter in range(iters)] for worker, iters in enumerate(num_seeds)]
    else:
        seed_lists = [seeds[int(i*process_iters):int((i+1)*process_iters)] for i in range(processes - 1)] + [seeds[int((processes-1)*process_iters):]]

    # Initiate processes
    qres = mp.Queue()
    workers = []
    for i in range(processes):
        workers.append(
            mp.Process(
                target=multiple,
                args=(process_iters, config, dec, go),
                kwargs={"qres": qres, "worker": i, "seeds": seed_lists[i], **kwargs},
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


def decoder_config(**kwargs):
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
        plot_nodes     = 0,
        plot_size      = 6,
        linewidth      = 1.5,
        scatter_size   = 30,
        z_distance     = 8,
    )

    for key, value in kwargs.items():
        if key in kwargs:
            kwargs[key] = value

    return config


if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(
        prog="OOPSC",
        description="simulation of surface code using mwpm/uf/eg decoder",
        usage='%(prog)s [-h] L'
        # formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument("lattice_size",
        action="store",
        type=int,
        help="size of the lattce",
        metavar="L",
    )

    sim = parser.add_argument_group("simulation", "arguments for simulation")

    sim.add_argument("-i", "--iters",
        action="store",
        type=int,
        default=1,
        help="number of iterations",
        metavar="",
    )

    sim.add_argument("-l", "--lattice_type",
        action="store",
        type=str,
        choices=["toric", "planar"],
        default="toric",
        help="type of lattice",
        metavar="",
    )

    sim.add_argument("-d", "--decoder",
        action="store",
        type=str,
        choices=["mwpm", "uf", "eg"],
        default="eg",
        help="type of decoder {mwpm/uf/eg}",
        metavar="",
    )

    sim.add_argument("-m", "--multithreading",
        action="store_true",
        help="use multithreading",
    )

    sim.add_argument("-px", "--paulix",
        action="store",
        type=float,
        default=0,
        help="Pauli X error rate",
        metavar="",
    )

    sim.add_argument("-pz", "--pauliz",
        action="store",
        type=float,
        default=0,
        help="Pauli Y error rate",
        metavar="",
    )

    sim.add_argument("-pmx", "--measurex",
        action="store",
        type=float,
        default=0,
        help="Measurement X error rate",
        metavar="",
    )

    sim.add_argument("-pmz", "--measurez",
        action="store",
        type=float,
        default=0,
        help="Measurement Y error rate",
        metavar="",
    )

    sim.add_argument("-pe", "--erasure",
        action="store",
        type=float,
        default=0,
        help="Erasure error rate",
        metavar="",
    )

    sim.add_argument("-s", "--seeds",
        action="store",
        type=int,
        nargs='*',
        help="seeds for the simulations (verbose)",
        metavar="",
    )

    parser_dec = parser.add_argument_group("decoder", "arguments for decoder")

    parser_dec.add_argument("-dgc", "--dg_connections",
        action="store_true",
        help="use dg_connections pre-union processing",
    )

    parser_dec.add_argument("-dg", "--directed_graph",
        action="store_true",
        help="use directed graph for evengrow",
    )

    plot_dec = parser.add_argument_group("figure", "arguments for plotting")

    plot_dec.add_argument("-p2d", "--plot2D",
        action="store_true",
        help="plot 2D lattice",
    )

    plot_dec.add_argument("-p3d", "--plot3D",
        action="store_true",
        help="plot 3D lattice",
    )

    plot_dec.add_argument("-puf", "--plotUF",
        action="store_true",
        help="plot uf-lattice",
    )

    plot_dec.add_argument("-pr", "--print_steps",
        action="store_true",
        help="print all debug info",
    )

    plot_dec.add_argument("-pf", "--plot_find",
        action="store_true",
        help="plot find cluster routine sequenctially",
    )

    plot_dec.add_argument("-pb", "--plot_bucket",
        action="store_true",
        help="plot growth routine by bucket",
    )

    plot_dec.add_argument("-pc", "--plot_cluster",
        action="store_true",
        help="plot growth routine by cluster",
    )

    plot_dec.add_argument("-pn", "--plot_node",
        action="store_true",
        help="plot growth routine by node",
    )

    plot_dec.add_argument("-pk", "--plot_cut",
        action="store_true",
        help="plot removed edges of cluster cycles",
    )

    plot_dec.add_argument("-pp", "--plot_peel",
        action="store_true",
        help="plot the peeling of edges sequentially",
    )

    plot_dec.add_argument("-ps", "--plot_size",
        action="store",
        type=int,
        default=6,
        help="size of plotting window",
        metavar=""
    )

    plot_dec.add_argument("-lw", "--linewidth",
        action="store",
        type=float,
        default=1.5,
        help="size of plotting window",
        metavar=""
    )

    plot_dec.add_argument("-ss", "--scatter_size",
        action="store",
        type=int,
        default=30,
        help="size of 3D plot scatter",
        metavar=""
    )

    plot_dec.add_argument("-zd", "--z_distance",
        action="store",
        type=int,
        default=8,
        help="distance between z layers in 3D plot",
        metavar=""
    )

    args=vars(parser.parse_args())
    decoder = args.pop("decoder")
    iters   = args.pop("iters")
    multi   = args.pop("multithreading")

    config = dict(
        ltype   = args.pop("lattice_type"),
        size    = args.pop("lattice_size"),
        pX      = args.pop("paulix"),
        pZ      = args.pop("pauliz"),
        pE      = args.pop("erasure"),
        pmX     = args.pop("measurex"),
        pmZ     = args.pop("measurez"),
    )

    if decoder == "mwpm":
        import mwpm as decode
    elif decoder == "uf":
        import unionfind as decode
    elif decoder == "eg":
        import unionfind_eg as decode

    if config["pmX"] == 0 and config["pmZ"] == 0:
        import graph_2D as go
    else:
        import graph_3D as go

    if iters == 1:
        output = single(args, decode, go, **config)
    elif not multi:
        output = multiple(iters, args, decode, go, **config)
    else:
        output = multiprocess(iters, args, decode, go, **config)

    pprint(output)
