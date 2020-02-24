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
        decoder = dec.toric(**config.decoder, **kwargs, plot_config=config.plot)
        graph = go.toric(size, decoder, plot2D=config.plot2D, plot3D=config.plot3D, plot_config=config.plot)
    elif type == "planar":
        decoder = dec.planar(**config.decoder, **kwargs, plot_config=config.plot)
        graph = go.planar(size, decoder, plot2D=config.plot2D, plot3D=config.plot3D, plot_config=config.plot)
    return decoder, graph


def get_mean_var(list_of_var, str):
    return {
        str+"_m": np.mean(list_of_var),
        str+"_v": np.std(list_of_var)
    }

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
        decoder, graph = lattice_type(ltype, config, dec, go, size, **kwargs)

    # Initialize errors
    if seed is None and config.seed is None:
        init_random_seed(worker=worker, iteration=iter)
    elif seed is not None:
        apply_random_seed(seed)
    elif config.seed is not None:
        apply_random_seed(config.seed)

    graph.apply_and_measure_errors(pX=pX, pZ=pZ, pE=pE, pmX=pmX, pmZ=pmZ)

    # Peeling decoder
    graph.decoder.decode()
    graph.decoder.get_counts()

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

    if seeds is None and config.seed is None:
        seeds = [init_random_seed(worker=worker, iteration=iter) for iter in range(iters)]

    elif config.seed is not None:
        if type(config.seed) == list:
            seeds = config.seed
        elif type(config.seed) == int:
            seeds = [config.seed] * iters
        else:
            raise TypeError

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
        #     "gbu"       : decoder.gbu,
        #     "gbo"       : decoder.gbo,
        #     "ufu"       : decoder.ufu,
        #     "uff"       : decoder.uff,
        #     "ctd"       : decoder.eg.ctd,
        #     "mac"       : decoder.eg.mac,
        }
        qres.put(output)
    else:
        output = {
            "N"         : iters,
            "succes"    : sum(result),
            **get_mean_var(graph.matching_weight, "weight"),
            **get_mean_var(decoder.time, "time"),
            # **get_mean_var(decoder.gbu, "gbu"),
            # **get_mean_var(decoder.gbo, "gbo"),
            # **get_mean_var(decoder.ufu, "ufu"),
            # **get_mean_var(decoder.uff, "uff"),
            # **get_mean_var(decoder.eg.ctd, "ctd"),
            # **get_mean_var(decoder.eg.mac, "mac")
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


class decoder_config(object):
    '''
    stores all settings of the decoder
    '''
    def __init__(self):

        self.plot2D = 1
        self.plot3D = 1
        self.seed = 3
        self.decoder = {
            "dg_connections": 0,
            "directed_graph": 0,
            "print_steps"   : 0,
            "plot_find"     : 1,
            "plot_growth"   : 0,
            "plot_peel"     : 1,
            "plot_nodes"    : 1,
        }

        self.plot = {
            "plot_size"     : 6,
            "line_width"    : 1.5,
            "plotstep_click": 1,
        }


if __name__ == "__main__":

    import unionfind as decode
    import graph_3D as go

    sim_config = {
        "ltype" : "toric",
        "size"  : 6,
        "pX"    : 0.03,
        "pZ"    : 0.0,
        "pE"    : 0.0,
        "pmX"   : 0.028,
        "pmZ"   : 0.0,
    }
    iters = 500

    output = single(decoder_config(), decode, go, **sim_config)
    # output = multiple(iters, decoder_config(), decode, go, **sim_config)

    pprint(output)
