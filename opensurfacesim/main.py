"""
Contains methods to run a simulated lattice of the surface code.
The graph type (2D/3D) and decoder (MWPM, unionfind...) are specified and are loaded.
One can choose to run a simulated lattice for a single, multiple or many (multithreaded) multiple iterations.

"""
from __future__ import annotations
from types import ModuleType
from typing import List, Optional, Tuple, Union
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
size_type = Union[Tuple[int, int], int]
errors_type = List[Union[str, Error]]
code_type = codes._template.sim.PerfectMeasurements
decoder_type = decoders._template.SimCode


def initialize(
    size: size_type,
    Code: module_or_name,
    Decoder: module_or_name,
    enabled_errors: errors_type = [],
    faulty_measurements: bool = False,
    plotting: bool = False,
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
        List of error modules from `.errors`.
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
    Code_flow = getattr(Code, "plot") if plotting else getattr(Code, "sim")
    Code_flow_dim = (
        getattr(Code_flow, "FaultyMeasurements")
        if faulty_measurements
        else getattr(Code_flow, "PerfectMeasurements")
    )

    if isinstance(Decoder, str):
        Decoder = getattr(decoders, Decoder)
    Decoder_flow = getattr(Decoder, "plot") if plotting else getattr(Decoder, "sim")
    Decoder_flow_code = getattr(Decoder_flow, Code.__name__.split(".")[-1].capitalize())

    code = Code_flow_dim(size, **kwargs)
    code.initialize(*enabled_errors)
    decoder = Decoder_flow_code(code, **kwargs)

    return code, decoder


def run(
    code: code_type,
    decoder: decoder_type,
    error_rates: dict = {},
    iterations: int = 1,
    plotting: bool = False,
    seed: Optional[float] = None,
    benchmark: Optional[BenchmarkDecoder] = None,
    mp_queue: Optional[Queue] = None,
    mp_process: int = 0,
    **kwargs,
):
    """Runs surface code simulation.

    Single command function to run a surface code simulation for a number of iterations.

    Parameters
    ----------
    code
        A surface code instance (see `initialize`).
    decoder
        A decoder instance (see `initialize`).
    iterations
        Number of iterations to run.
    error_rates
        Dictionary for error rates (see `~opensurfacesim.errors`).
    seed
        Float to use as the seed for the random number generator.
    benchmark
        Benchmarks decoder performance and analytics if attached.
    kwargs
        Keyword arguments are passed on to ``decoder.decode()``.

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
    if not seed:
        seed = timeit.default_timer()
    seed = float(f"{seed}{mp_process}")
    random.seed(seed)

    if benchmark:
        benchmark._set_decoder(decoder, seed=seed)

    output = {"no_error": 0}

    for iteration in range(iterations):
        print(f"Running iteration {iteration+1}/{iterations}", end="\r")
        code.random_errors(**error_rates)
        decoder.decode(**kwargs)
        logical_state = (
            code.logical_state
        )  # Must get logical state property to update code.no_error
        output["no_error"] += code.no_error
        if plotting:
            code.show_corrected()

    if plotting:
        code.figure.close()

    if benchmark:
        output.update(benchmark.data)
        output.update(benchmark.lists_mean_var())

    if mp_queue is None:
        return output
    else:
        mp_queue.put(output)


def run_multiprocess(
    code: code_type,
    decoder: decoder_type,
    error_rates: dict = {},
    iterations: int = 1,
    processes: int = 1,
    benchmark: Optional[BenchmarkDecoder] = None,
    **kwargs,
):
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
    error_rates
        Dictionary for error rates (see `~opensurfacesim.errors`).
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
                args=(code, decoder),
                kwargs={
                    "iterations": process_iters,
                    "mp_process": process,
                    "mp_queue": mp_queue,
                    "error_rates": error_rates,
                    "benchmark": benchmark ** kwargs,
                },
            )
        )
    print("Starting", processes, "workers.")

    # Start and join processes
    for worker in workers:
        worker.start()

    outputs = []
    for worker in workers:
        outputs.append(mp_queue.get())
        worker.join()

    output = {"no_error": 0}

    for partial_output in outputs:
        output["no_error"] += partial_output["no_error"]
    if benchmark:
        output["benchmark"] = []
        for partial_output in outputs:
            output[benchmark].append(partial_output["benchmark"])

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

    The benchmark class can also be attached to run. The mean and standard deviations of the benchmarked values are in that case updated to the output of run after running ``lists_mean_var``.

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

    list_decorators = ["duration"]
    value_decorators = ["count_calls"]

    def __init__(
        self, methods_to_benchmark: dict, decoder: Optional[decoder_type] = None, **kwargs
    ):
        self.decoder = decoder
        self.methods_to_benchmark = methods_to_benchmark
        self.data = {"decoded": 0, "iterations": 0, "seed": None}
        self.lists = defaultdict(list)
        self.values = defaultdict(float)
        if decoder:
            self._set_decoder(self, decoder, **kwargs)

    def _set_decoder(self, decoder: decoder_type, seed: Optional[float] = None, **kwargs):
        """Sets the benchmarked decoder and wraps its class methods."""
        self.decoder = decoder
        self.data["seed"] = seed

        # Wrap decoder.decode for check for ancillas after decoding
        decode = getattr(decoder, "decode")

        @wraps(decode)
        def wrapper(*args, **kwargs):
            result = decode(*args, **kwargs)
            self.data["decoded"] += decoder.code.trivial_ancillas
            self.data["iterations"] += 1
            return result

        setattr(decoder, "decode", wrapper)

        # Decorate decoder methods
        decorator_names = ["value_to_list"] + self.list_decorators + self.value_decorators
        for method_name, decorators in self.methods_to_benchmark.items():
            if isinstance(decorators, str):
                decorators = [decorators]

            class_method = getattr(decoder, method_name)
            for decorator in decorators:
                if decorator not in decorator_names:
                    raise NameError(f"Decorator {decorator} not defined.")
                wrapper = getattr(self, decorator)
                class_method = wrapper(class_method)
            setattr(decoder, method_name, class_method)

    def lists_mean_var(self, reset: bool = True):
        """Get mean and stand deviation of values in ``self.lists``.

        Parameters
        ----------
        reset
            Resets all in ``self.lists`` to empty lists.
        """
        processed_data = {}
        for decorated_method, data in self.lists.items():
            processed_data[f"{decorated_method}/mean"] = numpy.mean(data)
            processed_data[f"{decorated_method}/std"] = numpy.std(data)
        if reset:
            self.lists = defaultdict(list)
        return processed_data

    def value_to_list(self, func):
        """Appends all values in ``self.values`` to lists in ``self.lists``."""

        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            for decorated_method, value in self.values.items():
                self.lists[decorated_method].append(value)
            self.values = defaultdict(float)
            return result

        return wrapper

    def duration(self, func):
        """Logs the duration of ``func`` in ``self.lists``."""

        @wraps(func)
        def wrapper(*args, **kwargs):
            t = timeit.default_timer()
            result = func(*args, **kwargs)
            self.lists[f"duration/{func.__name__}"].append(timeit.default_timer() - t)
            return result

        return wrapper

    def count_calls(self, func):
        """Logs the number of calls to ``func`` in ``self.values``."""

        @wraps(func)
        def wrapper(*args, **kwargs):
            self.values[f"count_calls/{func.__name__}"] += 1
            return func(*args, **kwargs)

        return wrapper
