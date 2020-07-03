'''
2020 Mark Shui Hu

www.github.com/watermarkhu/OpenSurfaceSim
_____________________________________________

Contains methods to run a simulated lattice of the surface code.
The graph type (2D/3D) and decoder (MWPM, unionfind...) are specified and are loaded.
One can choose to run a simulated lattice for a single, multiple or many (multithreaded) multiple iterations.

'''
from progiter import ProgIter
import multiprocessing as mp
from decimal import Decimal as decimal
from collections import defaultdict as dd
from .info import printing as pr
import numpy as np
import random
import time
from simulator.configuration import sim_setup
from simulator.decoder._decorators import reset_counters


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


def apply_random_seed(seed, **kwargs):
    '''
    Applies a certain seed in the same format as init_random_seed()
    '''
    if not seed:
        seed = init_random_seed(**kwargs)
    if type(seed) is not decimal:
        seed = decimal(seed)
    random.seed(seed)


def get_mean_var(list_of_var, str):
    '''
    Calculates the total mean and variance of a number of means and variances
    '''
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
    code="toric",
    paulix=0,
    pauliz=0,
    erasure=0,
    measurex=0,
    measurez=0,
    decoder=None,
    graph=None,
    worker=0,
    iteration=0,
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
        graph = sim_setup(code, config, decoder, size, measurex, measurez, **kwargs)
        pr.print_configuration(config, 1, size=size, pX=paulix,
                               pZ=pauliz, pE=erasure, pmX=measurex, pmZ=measurez)
    # Initialize errors
    if seed is None and ("seeds" not in config or not config['seeds']):
        init_random_seed(worker=worker, iteration=iteration)
    elif seed is not None:
        apply_random_seed(seed, worker=worker, iteration=iteration)
    else:
        try:
            apply_random_seed(config["seeds"][0], worker=worker, iteration=iteration)
        except:
            raise IndexError("Seed list is empty")        

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
            try:
                print(graph.decoder.counters)
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
            except:
                raise RuntimeError("Debug not available in single mode")
    else:
        output = correct

    return output


def check_seeds(seeds, config, iters, **kwargs):
    '''
    Checks if the seeds provided either by seeds or the config['seeds'] is enough for the provided number of iters
    '''
    if seeds is None and ("seeds" not in config or not config['seeds']):
        seeds = [init_random_seed(iteration=i, **kwargs) for i in range(iters)]
    elif ("seeds" in config and config['seeds']):
        seeds = config["seeds"]

    if len(seeds) != iters:
        raise IndexError("Not enough seeds in config")
    return seeds


def multiple(
    size,
    config,
    iters,
    code="toric",
    paulix=0,
    pauliz=0,
    erasure=0,
    measurex=0,
    measurez=0,
    decoder=None,
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

    if graph is None:
        graph = sim_setup(code, config, decoder, size, measurex, measurez, **kwargs)
    
    info = True if worker == 0 else False

    pr.print_configuration(config, iters, size=size, paulix=paulix,
                               pauliz=pauliz, erasure=erasure, measurex=measurex, measurez=measurez, info=info)
    seeds = check_seeds(seeds, config, iters, worker=worker)

    options = dict(
        code=code,
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
            reset_counters(graph)
        return output
    else:
        output = dict(
            N         = iters,
            succes    = sum(result),
        )
        if debug:
            output.update(weight = graph.matching_weight)
            output.update(**graph.decoder.clist)
            reset_counters(graph)
        qres.put(output)


def multiprocess(
        size,
        config,
        iters,
        decoder=None,
        graphs=None,
        seeds=None,
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

    seeds = check_seeds(seeds, config, iters)
    process_seeds = [seeds[p*process_iters:(p+1)*process_iters] for p in range(processes)]

    # Initiate processes
    qres = mp.Queue()
    workers = []

    options = dict(
        decoder=decoder,
        qres=qres,
        called=0,
        debug=debug
    )

    if graphs is None or len(graphs) != processes:
        graphs = [None]*processes

    for i, (g, s) in enumerate(zip(graphs,  process_seeds), int(node*processes)):
        workers.append(
            mp.Process(
                target=multiple,
                args=(size, config, process_iters),
                kwargs=dict(worker=i, graph=g, seeds=s, **options, **kwargs),
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


