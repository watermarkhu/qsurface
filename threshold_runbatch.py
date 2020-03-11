'''
2020 Mark Shui Hu, QuTech

www.github.com/watermarkhu/oop_surface_code
_____________________________________________

'''

import oopsc
import sys
from oopsc import init_random_seed, single, get_mean_var
from decorators import debug as db
import multiprocessing as mp


def writeline(path, worker, line, type="a"):
    f = open(f"{path}{worker}.csv", type)
    f.write(line + "\n")
    print(line)
    f.close()

def get_columns():
    columns = [
        "L",
        "p",
        "N",
        "succes",
        "weight_m",
        "weight_v",
        "time_m",
        "time_v",
        "gbu_m",
        "gbu_v",
        "gbo_m",
        "gbo_v",
        "ufu_m",
        "ufu_v",
        "uff_m",
        "uff_v",
        "mac_m",
        "mac_v",
        "ctd_m",
        "ctd_v",
    ]
    return columns


def multiple(
    path,
    graph,
    size,
    config,
    iters,
    paulix=0,
    worker=0,
    debug=True,
    **kwargs
):
    """
    Runs the peeling decoder for a number of iterations. The graph is reused for speedup.
    """

    seeds = [init_random_seed(worker=worker, iteration=iter) for iter in range(iters)]

    options = dict(
        graph=graph,
        worker=worker,
        called=0,
        debug=True,
    )

    zipped = zip(range(iters), seeds)
    result = [single(size, config, paulix=paulix, iter=iter, seed=seed, **options, **kwargs) for iter, seed in zipped]

    output = dict(
        L       = size,
        p       = paulix,
        N       = iters,
        succes  = sum(result)
    )
    if debug:
        output.update(**get_mean_var(graph.matching_weight, "weight"))
        for key, value in graph.decoder.clist.items():
            output.update(**get_mean_var(value, key))
        db.reset_counters(graph)

    values = [str(output[key]) for key in get_columns()]

    writeline(path, worker, ",".join(values))


def multiprocess(
        path,
        graph,
        size,
        config,
        iters,
        processes,
        node=0,
        **kwargs
    ):
    """
    Runs the peeling decoder for a number of iterations, split over a number of processes
    """

    process_iters = iters // processes
    workers = []

    for i, g in enumerate(graph, int(node*processes)):
        workers.append(
            mp.Process(
                target=multiple,
                args=(path, g, size, config, process_iters),
                kwargs=dict(worker=i, **kwargs),
            )
        )
    print("Starting", processes, "workers.")

    for worker in workers:
        worker.start()

    for worker in workers:
        worker.join()


def run_thresholds(
        decoder,
        sim_name,
        node=0,
        lattice_type="toric",
        lattices = [],
        perror = [],
        iters = 0,
        processes=1,
        measurement_error=False,
        folder = "./",
        P_store=1000,
        debug=False,
        **kwargs
        ):
    '''
    ############################################
    '''

    if measurement_error:
        import graph_3D as go
    else:
        import graph_2D as go

    sys.setrecursionlimit(100000)

    progressbar = kwargs.pop("progressbar")

    int_P = [int(p*P_store) for p in perror]
    config = oopsc.default_config(**kwargs)

    path = folder + "/" + sim_name + "N"

    for i, _ in enumerate(range(processes), node*processes):
        writeline(path, i, ",".join(get_columns()), type="w")

    # Simulate and save results to file
    for lati in lattices:

        graph = [oopsc.lattice_type(lattice_type, config, decoder, go, lati) for _ in range(processes)]

        for pi, int_p in zip(perror, int_P):

            print("Calculating for L = ", str(lati), "and p =", str(pi))

            oopsc_args = dict(
                paulix=pi,
                lattice_type=lattice_type,
                debug=debug,
                progressbar=progressbar
            )
            if measurement_error:
                oopsc_args.update(measurex=pi)

            multiprocess(path, graph, lati, config, iters, processes, node, **oopsc_args)


if __name__ == "__main__":

    import argparse
    from oopsc import add_args

    parser = argparse.ArgumentParser(
        prog="threshold_run",
        description="run a threshold computation",
        usage='%(prog)s [-h/--help] decoder lattice_type iters -l [..] -p [..] (lattice_size)'
    )

    parser.add_argument("sim_name",
        action="store",
        type=str,
        help="same of sim",
        metavar="sim_name",
    )

    parser.add_argument("node",
        action="store",
        type=int,
        help="node number",
        metavar="node",
    )

    parser.add_argument("processes",
        action="store",
        type=int,
        help="number of processes",
        metavar="processes",
    )

    parser.add_argument("decoder",
        action="store",
        type=str,
        help="type of decoder - {mwpm/uf/eg}",
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

    pos_arguments= [
        ["-l", "--lattices", "store", "lattice sizes - verbose list int", dict(type=int, nargs='*', metavar="", required=True)],
        ["-p", "--perror", "store", "error rates - verbose list float", dict(type=float, nargs='*', metavar="", required=True)],
    ]

    key_arguments = [
        ["-f", "--folder", "store", "base folder path - toggle", dict(default="./", metavar="")],
        ["-me", "--measurement_error", "store_true", "enable measurement error (2+1D) - toggle", dict()],
        ["-ma", "--modified_ansatz", "store_true", "use modified ansatz - toggle", dict()],
        ["-pb", "--progressbar", "store_true", "enable progressbar - toggle", dict()],
        ["-dgc", "--dg_connections", "store_true", "use dg_connections pre-union processing - toggle", dict()],
        ["-dg", "--directed_graph", "store_true", "use directed graph for evengrow - toggle", dict()],
        ["-db", "--debug", "store_true", "enable debugging hearistics - toggle", dict()],
    ]

    add_args(parser, pos_arguments, "positional", "range of L and p values")
    add_args(parser, key_arguments)


    args=vars(parser.parse_args())
    decoder = args.pop("decoder")
    sim_name = args.pop("sim_name")


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


    run_thresholds(decode, sim_name, **args)
