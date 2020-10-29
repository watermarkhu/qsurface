from typing import Dict, List, Tuple, Union
from types import ModuleType
from .main import initialize, run, run_multiprocess, BenchmarkDecoder
from .errors._template import Sim as Error
from pathlib import Path
from pprint import pprint
from datetime import datetime
from scipy import optimize
import pandas as pd
import numpy as np
import sys


module_or_name = Union[ModuleType, str]


def format_output(output, category=""):
    formatted_output = {}
    for key, value in output.items():
        formatted_key = f"{category}/{key}" if category else key
        if isinstance(value, dict):
            formatted_output.update(format_output(value, formatted_key))
        else:
            formatted_output[formatted_key] = value
    return formatted_output


def sim_thresholds(
    Code: module_or_name,
    Decoder: module_or_name,
    iterations: int = 1,
    sizes: List[Union[int, Tuple[int, int]]] = [],
    enabled_errors: List[Union[str, Error]] = [],
    error_rates: List[Dict] = [],
    faulty_measurements: bool = False,
    methods_to_benchmark: dict = {},
    output: str = "",
    multiprocess: bool = False,
    mp_processes: int = 1,
    recursion_limit: int = 100000,
    **kwargs,
):
    """
    ############################################
    """
    sys.setrecursionlimit(recursion_limit)

    code_name = Code.__name__.split(".")[-1] if isinstance(Code, ModuleType) else Code
    decoder_name = Decoder.__name__.split(".")[-1] if isinstance(Decoder, ModuleType) else Code
    error_names = "/".join(
        [
            error.__name__.split(".")[-1] if isinstance(error, Error) else error
            for error in enabled_errors
        ]
    )

    if output == "":
        output = f"{code_name}_{decoder_name}-{error_names}.csv"
    output_path = Path(output)

    if output_path.exists():
        print(f"Loading existing file {output}.")
        data = read_csv(output_path)
    else:
        data = pd.DataFrame()

    runner = run_multiprocess if multiprocess else run

    # Simulate and save results to file
    for size in sizes:

        code, decoder = initialize(
            size, Code, Decoder, enabled_errors, faulty_measurements, **kwargs
        )

        for error_rate in error_rates:
            print(f"Running ({size}) lattice with error rates {error_rate}.")

            benchmarker = BenchmarkDecoder(methods_to_benchmark)

            output = runner(
                code,
                decoder,
                iterations=iterations,
                error_rates=error_rate,
                benchmark=benchmarker,
                mp_processes=mp_processes,
            )

            output.update(format_output(output.pop("benchmark")))
            output.update(
                {
                    "datetime": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                    "size": size,
                    "iterations": iterations,
                    **error_rate,
                }
            )
            pprint(output)

            data = data.append(output, ignore_index=True)
            data.to_csv(output_path)

    print(data.to_string())


def read_csv(file: str):
    file_path = Path(file)
    if file_path.exists():
        data = pd.read_csv(file_path, index_col=0)
    else:
        raise FileNotFoundError
    return data


def format_data(data: pd.DataFrame, column: str):

    sizes = sorted(list(set(data["size"])))
    rates = sorted(list(set(data[column])))

    simple_data = []
    for size in sizes:
        for rate in rates:
            iterations, no_error = 0, 0
            for _, row in data.loc[(data["size"] == size) & (data[column] == rate)].iterrows():
                iterations += row["iterations"]
                no_error += row["no_error"]
            simple_data.append([size, rate, iterations, no_error])

    simple_data = list(map(list, zip(*simple_data)))

    return simple_data


def fit_thresholds(file: str, column: str, modified_ansatz: bool = False):

    data = read_csv(file)
    sizes, rates, iterations, no_error = format_data(data, column)

    def fit_func(PL, pth, A, B, C, D, nu, mu):
        p, L = PL
        x = (p - pth) * L ** (1 / nu)
        return A + B * x + C * x ** 2

    def fit_func_m(PL, pth, A, B, C, D, nu, mu):
        p, L = PL
        x = (p - pth) * L ** (1 / nu)
        return A + B * x + C * x ** 2 + D * L ** (-1 / mu)

    min_rate, max_rate = min(rates), max(rates)
    g_T, T_m, T_M = (min_rate + max_rate) / 2, min_rate, max_rate
    g_A, A_m, A_M = 0, -np.inf, np.inf
    g_B, B_m, B_M = 0, -np.inf, np.inf
    g_C, C_m, C_M = 0, -np.inf, np.inf
    gnu, num, nuM = 0.974, 0.8, 1.2
    D_m, D_M = -2, 2
    mum, muM = 0, 3
    g_D, gmu = 1.65, 0.71

    par_guess = [g_T, g_A, g_B, g_C, g_D, gnu, gmu]
    bound = [(T_m, A_m, B_m, C_m, D_m, num, mum), (T_M, A_M, B_M, C_M, D_M, nuM, muM)]

    fit = fit_func_m if modified_ansatz else fit_func

    parameters, covariance = optimize.curve_fit(
        fit,
        (rates, sizes),
        [num / iters for num, iters in zip(no_error, iterations)],
        par_guess,
        bounds=bound,
        sigma=[max(iterations) / iters for iters in iterations],
    )
    error = np.sqrt(np.diag(covariance))
    print(f"Fitted threshold at {column}={parameters[0]}+-{error[0]}")

    return parameters
