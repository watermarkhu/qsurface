"""
Contains methods to run a simulated lattice of the surface code.
The graph type (2D/3D) and decoder (MWPM, unionfind...) are specified and are loaded.
One can choose to run a simulated lattice for a single, multiple or many (multithreaded) multiple iterations.

"""
from __future__ import annotations
from types import ModuleType
from typing import List, Optional, Union
from collections import defaultdict
from functools import wraps
from multiprocessing import Process, Queue, cpu_count
import timeit
import random
import numpy
from . import decoders
from . import codes
from .errors._template import Sim as Error


module_or_name = Union[ModuleType, str]


def initialize(
    size,
    Code: module_or_name,
    Decoder: module_or_name,
    enabled_errors: List[Union[str, Error]] = [],
    faulty_measurements: bool = False,
    show_plots: bool = False,
    **kwargs,
):  
    """Initializes a code and a decoder.

    Parameters
    ----------
    size
        The size of the surface in xy or (x,y).
    Code
        Any surface code module or module name from codes.
    Decoder
        Any decoder module or module name from decoders
    enabled_errors
        List of error modules from errors.
    faulty_measurements
        Enable faulty measurements (decode in a 3D lattice).
    plotting
        Enable plotting for the surface code and/or decoder.
    kwargs
        Keyword arguments are passed on to the chosen code and decoder.

    Examples
    --------
    To initialize a 6x6 toric code with the MWPM decoder and Pauli errors:

        >>> initialize((6,6), "toric", "mwpm", enabled_errors=["pauli"], check_compatibility=True)
        (<toric (6, 6) PerfectMeasurements>,  <Minimum-Weight Perfect Matching decoder (Toric)>)
        ✅ This decoder is compatible with the code.
    """


    if isinstance(Code, str):
        Code = getattr(codes, Code)
    Code_flow = getattr(Code, "plot") if show_plots else getattr(Code, "sim")
    Code_flow_dim = (
        getattr(Code_flow, "FaultyMeasurements")
        if faulty_measurements
        else getattr(Code_flow, "PerfectMeasurements")
    )

    if isinstance(Decoder, str):
        Decoder = getattr(decoders, Decoder)
    Decoder_flow = getattr(Decoder, "plot") if show_plots else getattr(Decoder, "sim")
    Decoder_flow_code = getattr(Decoder_flow, Code.__name__.split(".")[-1].capitalize())

    code = Code_flow_dim(size, **kwargs)
    decoder = Decoder_flow_code(code, **kwargs)
    code.initialize(*enabled_errors)

    return code, decoder


def run(
    size,
    Code: module_or_name = "toric",
    Decoder: module_or_name = "mwpm",
    enabled_errors: List[Union[str, Error]] = [],
    error_rates: dict = {},
    iterations: int = 1,
    faulty_measurements: bool = False,
    show_plots: bool = False,
    seed_prefix: str = "",
    benchmark: Optional[BenchmarkDecoder] = None,
    multiprocessing_queue: Optional[Queue] = None,
    **kwargs,
):
    """Runs surface code simulation.

    Single command function to run a surface code simulation for a number of iterations.

    Parameters
    ----------
    code
        A surface code instance (see initialize).
    decoder
        A decoder instance (see initialize).
    iterations
        Number of iterations to run.
    error_rates
        Dictionary for error rates (see errors).
    seed
        Float to use as the seed for the random number generator.
    benchmark
        Benchmarks decoder performance and analytics if attached.
    kwargs
        Keyword arguments are passed on to initialize.

    Examples
    --------
    To simulate the toric code and simulate with bitflip error for 10 iterations and decode with the MWPM decoder:

        >>> code, decoder = initialize((6,6), "toric", "mwpm", enabled_errors=["pauli"])
        >>> run(code, decoder, iterations=10, error_rates = {"p_bitflip": 0.1})
        {'no_error': 8}

    Benchmarked results are updated to the returned dictionary. See BenchmarkDecoder for the syntax and information to setup benchmarking.

        >>> benchmarker = BenchmarkDecoder({"decode":"duration"})
        >>> run(code, decoder, iterations=10, error_rates = {"p_bitflip": 0.1}, benchmark=benchmarker)
        {'no_error': 8,
        'benchmark': {'success_rate': [10, 10],
        'seed': 12447.413636559,
        'durations': {'decode': {'mean': 0.00244155000000319,
        'std': 0.002170364089572033}}}}
    """
    # Initialize lattice

    code, decoder = initialize(
        size, Code, Decoder, enabled_errors, faulty_measurements, show_plots, **kwargs
    )
    if benchmark:
        benchmark.add_cls_instance(decoder)

    seed = seed_prefix + str(timeit.default_timer())

    output = {"no_error": 0, "decoded": 0}

    for iteration in range(iterations):
        print(f"Running iteration {iteration}/{iterations}", end="\r")
        code.random_errors(**error_rates)
        decoder.decode()
        if show_plots:
            code.show_corrected()
        logical_state = code.logical_state
        output["no_error"] += code.no_error
        output["decoded"] += decoder.successfully_decoded

    if multiprocessing_queue is None:
        return output
    else:
        multiprocessing_queue.put(output)


def run_multiprocess(size, iterations: int = 1, processes: Optional[int] = None, **kwargs):
    """Runs surface code simulation using multiple processes.

    Using the standard module `multiprocessing` and its `~multiprocessing.Process` class, several processes are created that each runs its on contained simulation using `run`. The ``code`` and ``decoder`` objects are copied such that each process has its own instance. The total number of ``iterations`` are divided for the number of ``processes`` indicated. If no ``processes`` parameter is supplied, the number of available threads is determined via `~multiprocessing.cpu_count` and all threads are utilized.

    If a `~BenchmarkDecoder` object is attached, `~multiprocessing.Process` copies the object for each separate thread. Each instance of the the decoder thus have its own benchmark object. The results of the benchmark are appended to a list and addded to the output.

    See `run` for examples on running a simulation.

    Parameters
    ----------
    code
        A surface code instance (see initialize).
    decoder
        A decoder instance (see initialize).
    iterations
        Total number of iterations to run.
    processes
        Number of processes to spawn.
    benchmark
        Benchmarks decoder performance and analytics if attached.
    kwargs
        Keyword arguments are passed on to every process of run.
    """

    if processes is None:
        processes = cpu_count()
    process_iters = iterations // processes
    if process_iters == 0:
        print("Please select more iterations")
        return

    # Initiate processes
    mp_queue = Queue()
    workers = []
    for process in range(processes):
        workers.append(
            Process(
                target=run,
                args=(size,),
                kwargs={
                    "iterations": process_iters,
                    "seed_prefix": f"P{process}",
                    "multiprocessing_queue": mp_queue,
                    **kwargs,
                },
            )
        )
    print("Starting", processes, "workers.")

    # Start and join processes
    for worker in workers:
        worker.start()

    output = {"no_error": 0, "decoded": 0}

    for worker in workers:
        partial_output = mp_queue.get()
        output["no_error"] += partial_output["no_error"]
        output["decoded"] += partial_output["decoded"]

    return output


class BenchmarkDecoder(object):
    """Benchmarks a decoder during simulation.

    A benchmark of a decoder can be performed by attaching the current class to a ``decode``r. A benchmarker will keep track of the number of simulated iterations and the number of successfull operations by the decoder in ``self.data``.

    Secondly, a benchmark of the decoder’s class methods can be performed by the decorators supplied in the current class, which have the form def ``decorator(self, func):``. The approach in the current benchmark class allows for decorating any of the decoder’s class methods after it has been instanced. The benefit here is that if no benchmark class is attached, no benchmarking will be performed. The class methods to benchmark must be supplied as a dictionary, where the keys are equivalent to the class method names, and the values are the decorator names. Benchmarked values are stored as class attributes to the benchmark object.

    There are two types of decorators, list decorators, which append some value to a dictionary of lists ``self.lists``, and value decorators, that saves or updates some value in ``self.values``.

    Parameters
    ----------
    methods_to_benchmark
        Decoder class methods to benchmark.
    decoder
        Decoder object.
    seed
        Logged seed of the simulation.

    Attributes
    ----------
    data
        Simulation data.
    lists
        Benchmarked data by list decorators.
    values
        Benchmarked data by value decorators.

    Examples
    --------
    To keep track of the duration of each iteration of decoding, the decoder’s decode method can be decorated with the duration decorator.

        >>> code, decoder = initialize((6,6), "toric", "mwpm", enabled_errors=["pauli"])
        >>> benchmarker = BenchmarkDecoder({"decode": "duration"}, decoder=decoder)
        >>> code.random_errors(p_bitflip=0.1)
        >>> decoder.decode()
        >>> benchmarker.lists
        {'duration': {'decode': [0.0009881999976641964]}}

    The benchmark class can also be attached to run. The mean and standard deviations of the benchmarked values are in that case updated to the output of run after running list_mean_var.

        >>> benchmarker = BenchmarkDecoder({"decode":"duration"})
        >>> run(code, decoder, iterations=10, error_rates = {"p_bitflip": 0.1}, benchmark=benchmarker)
        {'no_error': 8,
        'benchmark': {'success_rate': [10, 10],
        'seed': 12447.413636559,
        'durations': {'decode': {'mean': 0.00244155000000319,
            'std': 0.002170364089572033}}}}

    Number of calls to class methods can be counted by the count_calls decorator and stored to self.values. Values in self.values can be saved to a list to, for example, log the value per decoding iteration by the value_to_list decorator. Multiple decorators can be attached to a class method by a list of names in methods_to_benchmark. The logged data are still available in the benchmarker class itself.

        >>> benchmarker = BenchmarkDecoder({
        "decode": ["duration", "value_to_list"],
        "correct_edge": "count_calls",
        })
        >>> run(code, decoder, iterations=10, error_rates = {"p_bitflip": 0.1}, benchmark=benchmarker)
        {'no_error': 8,
        'benchmark': {'success_rate': [10, 10],
        'seed': '12447.413636559',
        'duration': {'decode': {'mean': 0.001886229999945499,
            'std': 0.0007808582199605158}},
        'count_calls': {'correct_edge': {'mean': 6.7, 'std': 1.4177446878757827}}}}
        >>> benchmarker.lists
            {'duration': {'decode': [0.0030814000019745436,
            0.0015807000017957762,
            0.0010604999988572672,
            0.0035383000031288248,
            0.0018329999984416645,
            0.001753099997586105,
            0.001290500000322936,
            0.0014110999982221983,
            0.0011783000009017996,
            0.0021353999982238747]},
            'count_calls': {'correct_edge': [10, 7, 5, 7, 6, 6, 7, 6, 5, 8]}}

    Nested class methods can also be benchmarked, e.g. for find of Cluster, which has an alias in unionfind.sim.Toric.

        >>> code, decoder = initialize((6,6), "toric", "unionfind", enabled_errors=["pauli"])
        >>> benchmarker = BenchmarkDecoder({"Cluster.find", "count_calls"})
        >>> code.random_errors(p_bitflip=0.1)
        >>> decoder.decode()
        >>> benchmarker.values
        {'count_calls': {'find': 30}}
    """
    def __init__(self, cls_methods_to_benchmark: dict, multiprocess:bool=False, **kwargs):
        self.operations = cls_methods_to_benchmark
        self.cls_instances = []
        self.data = {
            "durations": defaultdict(list),
            "num_calls": defaultdict(list),
            "call_count": defaultdict(int),
        }

    def add_cls_instance(self, cls_instance):
        for cls_instance_method, bench_method in self.operations.items():
            wrapper = getattr(self, bench_method)
            setattr(
                cls_instance,
                cls_instance_method,
                wrapper(getattr(cls_instance, cls_instance_method)),
            )
        cls_instance.benchmarker = self
        self.cls_instances.append(cls_instance)


    def get_mean_var(self, reset: bool = True):
        processed_data = {}
        for wrapper, wrapper_data in self.data.items():
            if wrapper_data.default_factory is list:
                benchmarked_data = {}
                for method, method_data in wrapper_data.items():
                    benchmarked_data[method] = {
                        "mean": numpy.mean(method_data),
                        "std": numpy.std(method_data),
                    }
                if reset:
                    self.data[wrapper] = defaultdict(list)
                if benchmarked_data:
                    processed_data[wrapper] = benchmarked_data
        return processed_data

    def duration(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            t = timeit.default_timer()
            result = func(*args, **kwargs)
            self.data["durations"][func.__name__].append(timeit.default_timer() - t)
            return result

        return wrapper

    def count_calls(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            self.data["call_count"][func.__name__] += 1
            return func(*args, **kwargs)

        return wrapper

    def save_calls(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            for name, calls in self.data["call_count"].items():
                self.data["num_calls"][name].append(calls)
                self.data["call_count"][name] = 0
            return result

        return wrapper
