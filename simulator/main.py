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
from .info.decorators import debug as db
import numpy as np
import random
import time
from simulator.helper import sim_setup


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


def lattice_type(code, config, dec, go, size, **kwargs):
    '''
    Initilizes the graph and decoder type based on the lattice structure.
    '''

    if type(dec) == str:
        try:
            decoders = __import__("simulator.decoder", fromlist=[dec])
            dec = getattr(decoders, dec)
        except:
            print("Decoder type invlid")
    try:
        decoder = getattr(dec, code)(**config, **kwargs)
    except:
        print("Graph type not defined in decoder class")

    graph = getattr(go, code)(size, decoder, **config, **kwargs)
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
    code="toric",
    paulix=0,
    pauliz=0,
    erasure=0,
    measurex=0,
    measurez=0,
    dec=None,
    # go=None,
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
        graph = sim_setup(code, config, dec, size, measurex, measurez, **kwargs)


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
            try:
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
                print("Debug not available in single mode")
    else:
        output = correct

    return output


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
    dec=None,
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
        graph = sim_setup(code, config, dec, size, measurex, measurez, **kwargs)


    if seeds is None and not config["seeds"]:
        seeds = [init_random_seed(worker=worker, iteration=iter) for iter in range(iters)]
    elif not config["seeds"]:
        seeds = config["seeds"]

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


