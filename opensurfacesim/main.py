'''
Contains methods to run a simulated lattice of the surface code.
The graph type (2D/3D) and decoder (MWPM, unionfind...) are specified and are loaded.
One can choose to run a simulated lattice for a single, multiple or many (multithreaded) multiple iterations.

'''
from .configuration2 import setup_decoder
from progiter import ProgIter
import multiprocessing as mp
from collections import defaultdict as dd
from .info import printing as pr
import numpy as np
import random
import time


def init_random_seed(seed=None, **kwargs):
    '''
    Initializes random with a seed

    If no `seed` is provided, the current timestamp from `time.time()` is used as the seed

    Parameters
    ----------
    seed : optional
    '''
    if seed is None:
        seed = time.time()
    random.seed(seed)


def get_mean_var(dict_values, result={}, **kwargs):
    '''
    Calculates the means and variances of a number of lists of values. 

    For every key and item (list of values) in `dict_values`, the mean and variance of the values are stored in the `result` dictionary at with the keys `key_m`, `key_v`, respectively. If a `result` dictionary is provided as input, the mean and variance values are updated to this dictionary and outputted. 

    Parameters
    ----------
    dict_values : dict of lists
        Dictionary with lists of values on which the mean and variance are calculated.
    result : dict, optional
        Dictionary in which the means and variances are stored

    Examples
    --------
    >>> get_mean_var({"foo": [1,2], "bar": [1,2,3,4,5]})
    {
        "foo_m": 1.5,
        "foo_v": 0.25,
        "bar_m": 3.0,
        "bar_v": 2.0
    }
    '''
    for key, list_values in dict_values.items():
        if list_values:
            result.update({
                key+"_m": np.mean(list_values),
                key+"_v": np.var(list_values)
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
    seed=None,
    benchmark=False,
    called=True,
    decoder=None,
    **kwargs
):
    """
    Runs the surface code simulation for one iteration

    Parameters
    ----------

    size : int
        One-dimensional length of the surface.
    code : str, optional
        Type of surface code. Name must be equivalent to a code included in `opensurfacesim.code` as `{code}.py`. 
    decode_module : str, optional
        Type of decoder. Name must equivalent to a decoder included in `opensurfacesim.decoder` as `{decoder}.py`. 
    error_rates : dict, optional
        Dictionary of included error rates. The keys of this dictionary must be equivalent to one of the keys of the `apply_error()` methods in the error modules in `opensurfacesim.error`.
    perfect_measurments : bool, optional
        Toggle of enabling perfect measurements. ## TODO remove this, must be included in `error_rates`.
    seed : optional
        The seed used for the `random` module. 
    benchmark : bool, optional
        Toggle for adding benchmarking tools to the simulation. See `opensurfacesim.info.benchmark`.
    called, decoder
        Parameters used when `single` is called by the `multiple` method. 

    Examples
    --------
    >>> single(8, code="toric", decode_module="mwpm", error_rates={"paulix":0.1})
    ___________________________________________________________________________
    OpenSurfaceSim
    2020 Mark Shui Hu
    https://github.com/watermarkhu/OpenSurfaceSim
    ...........................................................................
    Decoder type: Minimum-Weight Perfect Matching (networkx)
    Graph type: 2D toric
    ...........................................................................
    Simulation using settings:
    {'iterations': 1, 'paulix': 0.1, 'size': 8}
    ...........................................................................
    {'succes': True}
    
    """
    # Initialize lattice
    if decoder is None:
        decoder = setup_decoder(code, decode_module, size, perfect_measurements, benchmark, **kwargs)
        pr.print_configuration(1, size=size, **error_rates)

    # Initialize errors
    if seed is None:
        init_random_seed()
    else:
        if type(seed) not in [float, int, str]:
            raise TypeError("Seed type error. Check if single seed given.")
        apply_random_seed(seed)
       
    decoder.graph.apply_and_measure_errors(**error_rates)
    decoder.decode()
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

    options = dict(
        error_rates=error_rates,
        decoder=decoder,
        called=0,
        benchmark=benchmark
    )

    iterator = ProgIter(range(iters)) if progressbar else range(iters)
    result = [single(size, **options, **kwargs) for iter in iterator]

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

    # Initiate processes
    qres = mp.Queue()
    workers = []

    options = dict(
        qres=qres,
        called=0,
    )

    if decoder is None or len(decoder) != processes:
        decoder = [None]*processes

    for i, pdec in enumerate(decoder):
        workers.append(
            mp.Process(
                target=multiple,
                args=(size, process_iters),
                kwargs=dict(worker=i, decoder=pdec, **options, **kwargs)
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


