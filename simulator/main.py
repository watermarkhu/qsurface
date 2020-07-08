'''
2020 Mark Shui Hu

www.github.com/watermarkhu/OpenSurfaceSim
_____________________________________________

Contains methods to run a simulated lattice of the surface code.
The graph type (2D/3D) and decoder (MWPM, unionfind...) are specified and are loaded.
One can choose to run a simulated lattice for a single, multiple or many (multithreaded) multiple iterations.

'''
from simulator.configuration import setup_decoder
from progiter import ProgIter
import multiprocessing as mp
from decimal import Decimal as decimal
from collections import defaultdict as dd
from .info import printing as pr
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


def apply_random_seed(seed, **kwargs):
    '''
    Applies a certain seed in the same format as init_random_seed()
    '''
    if not seed:
        seed = init_random_seed(**kwargs)
    if type(seed) is not decimal:
        seed = decimal(seed)
    random.seed(seed)


def get_mean_var(dict_values, result={}, **kwargs):
    '''
    Calculates the total mean and variance of a number of means and variances
    '''
    for key, list_values in dict_values.items():
        if list_values:
            result.update({
                key+"_m": np.mean(list_values),
                key+"_v": np.std(list_values)
            })
        else:
            result.update({key+"_m": 0, key+"_v": 0})
    return result
            

def single(
    size,
    code="toric",
    decode_module='mwpm',
    error_rates = {},
    perfect_measurements=True,
    decoder=None,
    worker=0,
    iteration=0,
    seed=None,
    called=True,
    benchmark=False,
    **kwargs
):
    """
    Runs the peeling decoder for one iteration
    """
    # Initialize lattice
    if decoder is None:
        decoder = setup_decoder(code, decode_module, size, perfect_measurements, 
            benchmark=benchmark, **kwargs)
        pr.print_configuration(1, size=size, **error_rates)
    # Initialize errors
    if seed is None:
        init_random_seed(worker=worker, iteration=iteration)
    else:
        if type(seed) not in [float, int, str]:
            raise TypeError("Seed type error. Check if single seed given.")
        apply_random_seed(seed, worker=worker, iteration=iteration)
       
    decoder.graph.apply_and_measure_errors(**error_rates)

    # Peeling decoder
    decoder.decode()

    # Measure logical operator
    logical_error, correct = decoder.graph.logical_error()
    decoder.reset()

    if called:
        output = dict(succes=correct)
        if benchmark:
            output.update(**decoder.benchmarker.counters)
    else:
        output = correct
        if benchmark:
            decoder.benchmarker.get_counters()

    return output


def check_seeds(seed, iters, **kwargs):
    '''
    Checks if the seeds provided either by seeds or the config['seeds'] is enough for the provided number of iters
    '''
    if seed is None:
        seed = [init_random_seed(iteration=1, **kwargs)
            for i in range(iters)]
    else:
        if type(seed) != list:
            raise TypeError("Must supply a list of seeds")

        if len(seed) != iters:
            raise IndexError("Not enough seeds in config")

    return seed


def multiple(
    size,
    iters,
    code="toric",
    decode_module="mwpm",
    error_rates={},
    perfect_measurements=True,
    decoder=None,
    qres=None,
    worker=0,
    seed=None,
    called=True,
    progressbar=True,
    benchmark=False,
    **kwargs
):
    """
    Runs the peeling decoder for a number of iterations. The graph is reused for speedup.
    """

    if decoder is None:
        info = True if worker == 0 else False
        decoder = setup_decoder(code, decode_module, size,
            perfect_measurements, benchmark=benchmark, info=info, **kwargs)
        if info:
            pr.print_configuration(iters, size=size, **error_rates)

    seed = check_seeds(seed, iters, worker=worker)

    options = dict(
        error_rates=error_rates,
        decoder=decoder,
        worker=worker,
        called=0,
        benchmark=benchmark
    )
    

    zipped = zip(ProgIter(range(iters)), seed) if progressbar else zip(range(iters), seed)
    result = [single(size, iteration=iter, seed=ss, **options, **kwargs) for iter, ss in zipped]

    if called:
        output = dict(
            N       = iters,
            succes  = sum(result)
        )
        if benchmark:
            output = get_mean_var(decoder.benchmarker.clist, output)
            decoder.benchmarker.reset_clist()
        return output
    else:
        output = dict(
            N         = iters,
            succes    = sum(result),
        )
        if benchmark:
            output.update(**decoder.benchmarker.clist)
            decoder.benchmarker.reset_clist()
        qres.put(output)


def multiprocess(
        size,
        iters,
        decoder=None,
        seed=None,
        processes=None,
        node=0,
        **kwargs
    ):
    """
    Runs the peeling decoder for a number of iterations, split over a number of processes
    """

    if processes is None:
        processes = mp.cpu_count()

    # Calculate iterations for ieach child process
    process_iters = iters // processes

    seed = check_seeds(seed, iters)
    process_seeds = [seed[p*process_iters:(p+1)*process_iters] 
        for p in range(processes)]

    # Initiate processes
    qres = mp.Queue()
    workers = []

    options = dict(
        qres=qres,
        called=0,
    )

    if decoder is None or len(decoder) != processes:
        decoder = [None]*processes

    for i, (pseed, pdec) in enumerate(zip(process_seeds, decoder)):
        workers.append(
            mp.Process(
                target=multiple,
                args=(size, process_iters),
                kwargs=dict(worker=i, seed=pseed, decoder=pdec, **options, **kwargs)
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

    output = get_mean_var(workerlists, output)

    for worker in workers:
        worker.join()

    return output


