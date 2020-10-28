"""
Contains methods to run a simulated lattice of the surface code.
The graph type (2D/3D) and decoder (MWPM, unionfind...) are specified and are loaded.
One can choose to run a simulated lattice for a single, multiple or many (multithreaded) multiple iterations.

"""
from types import ModuleType
from typing import List, Optional, Union
from collections import defaultdict
from functools import wraps
from multiprocessing import Manager, Process, Queue, cpu_count
import timeit
import random
import numpy
from . import decoders
from . import codes
from .errors._template import Sim as Error


module_or_name = Union[ModuleType, str]


class BenchmarkDecoder(object):
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


def init_random_seed(seed_prefix: int = "", **kwargs):
    """
    Initializes random with a seed

    If no `seed` is provided, the current timestamp from `time.time()` is used as the seed

    Parameters
    ----------
    seed : optional
    """
    seed = seed_prefix + str(timeit.default_timer())
    random.seed(seed)
    return seed


def initialize(
    size,
    Code: module_or_name,
    Decoder: module_or_name,
    enabled_errors: List[Union[str, Error]] = [],
    faulty_measurements: bool = False,
    show_plots: bool = False,
    **kwargs,
):
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
    """
    # Initialize lattice

    code, decoder = initialize(
        size, Code, Decoder, enabled_errors, faulty_measurements, show_plots, **kwargs
    )
    if benchmark:
        benchmark.add_cls_instance(decoder)

    output = {"no_error": 0, "decoded": 0}

    for iteration in range(iterations):
        print(f"Running iteration {iteration}/{iterations}", end="\r")
        init_random_seed(seed_prefix)
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
    """
    Runs the peeling decoder for a number of iterations, split over a number of processes
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