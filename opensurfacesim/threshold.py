from typing import Dict, List, Tuple, Union, Optional
from types import ModuleType
from dataclasses import dataclass
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.figure import Figure
from pathlib import Path
from pprint import pprint
from datetime import datetime
from scipy import optimize
import pandas as pd
import numpy as np
import sys
from .main import initialize, run, run_multiprocess, BenchmarkDecoder
from .errors._template import Sim as Error


module_or_name = Union[ModuleType, str]
formatted_dataframe = Tuple[list, list, list, list]
plt_markers = ["o", "s", "v", "D", "p", "^", "h", "X", "<", "P", "*", ">", "H", "d"] + [i + 4 for i in range(7)]
fit_param = Tuple[float, float, float]


def run_many(
    Code: module_or_name,
    Decoder: module_or_name,
    iterations: int = 1,
    sizes: List[Union[int, Tuple[int, int]]] = [],
    enabled_errors: List[Union[str, Error]] = [],
    error_rates: List[Dict] = [],
    faulty_measurements: bool = False,
    methods_to_benchmark: dict = {},
    output: str = "",
    mp_processes: int = 1,
    recursion_limit: int = 100000,
    **kwargs,
) -> Optional[pd.DataFrame]:
    """Runs a series of simulations of varying sizes and error rates.

    A series of simulations are run without plotting for all combinations of ``sizes`` and ``error_rates``. The results are returned as a Pandas DataFrame and saved to the working directory as a csv file. If an existing csv file with the same file name is found, the existing file is loaded and new results are appended to the existing data. A `.main.BenchmarkDecoder` object is attached to each simulation to log the seed and other information.

    Parameters
    ----------
    Code
        Any surface code module or module name from codes.
    Decoder
        Any decoder module or module name from decoders
    iterations
        Number of iterations to run per configuration.
    sizes
        The sizes of the surface configurations.
    enabled_errors
        List of error modules from `.errors`.
    error_rates
        List of dictionaries for error rates per configuration (see `~opensurfacesim.errors`).
    faulty_measurements
        Enable faulty measurements (decode in a 3D lattice).
    methods_to_benchmark
        Decoder class methods to benchmark.
    output
        File name of outputted csv data. If set to "none", no file will be saved.
    mp_processses
        Number of processes to spawn. For a single process, `~.main.run` is used. For multiple processes, `~main.run_multiprocess` is utilized.

    Examples
    --------
    A series of simulations using the ``toric`` surface code and ``mwpm`` decoder can be easily setup. Benchmarking can be performed by supplying the ``methods_to_benchmark`` argument of the `~.main.BenchmarkDecoder` class. The function will initialize a benchmark object of each configuration and append all results as columns to the returned dataframe. 

        >>> data = run_many(
        ...     "toric",
        ...     "mwpm",
        ...     iterations = 1000,
        ...     sizes = [8,12,16],
        ...     enabled_errors = ["pauli"],
        ...     error_rates = [{"p_bitflip: p} for p in [0.09, 0.1, 0.11]],
        ... )
        >>> print(data)
                        datetime  decoded    iterations  no_error  p_bitflip          seed  size  
        0   04/11/2020 14:45:36   1000.0        1000.0     820.0       0.09  13163.013981   8.0  
        1   04/11/2020 14:45:45   1000.0        1000.0     743.0       0.10  13172.277886   8.0  
        2   04/11/2020 14:45:54   1000.0        1000.0     673.0       0.11  13181.090130   8.0  
        3   04/11/2020 14:46:36   1000.0        1000.0     812.0       0.09  13190.191461  12.0  
        4   04/11/2020 14:47:18   1000.0        1000.0     768.0       0.10  13232.408302  12.0  
        5   04/11/2020 14:48:16   1000.0        1000.0     629.0       0.11  13274.044268  12.0  
        6   04/11/2020 14:51:47   1000.0        1000.0     855.0       0.09  13332.153639  16.0  
        7   04/11/2020 14:55:15   1000.0        1000.0     754.0       0.10  13542.533067  16.0  
        8   04/11/2020 14:59:14   1000.0        1000.0     621.0       0.11  13751.082511  16.0

    


    """
    sys.setrecursionlimit(recursion_limit)

    code_name = Code.__name__.split(".")[-1] if isinstance(Code, ModuleType) else Code
    decoder_name = Decoder.__name__.split(".")[-1] if isinstance(Decoder, ModuleType) else Code
    error_names = "/".join([error.__name__.split(".")[-1] if isinstance(error, Error) else error for error in enabled_errors])

    if output == "":
        output = f"{code_name}_{decoder_name}-{error_names}.csv"

    output_path = Path(output)

    if output_path.exists():
        print(f"Loading existing file {output}.")
        data = read_csv(output_path)
    else:
        data = pd.DataFrame()

    runner = run_multiprocess if mp_processes > 1 else run

    # Simulate and save results to file
    for size in sizes:

        code, decoder = initialize(size, Code, Decoder, enabled_errors, faulty_measurements, **kwargs)

        for error_rate in error_rates:
            print(f"Running ({size}) lattice with error rates {error_rate}.")

            benchmarker = BenchmarkDecoder(methods_to_benchmark)

            result = runner(
                code,
                decoder,
                iterations=iterations,
                error_rates=error_rate,
                benchmark=benchmarker,
                mp_processes=mp_processes,
            )

            result.update(
                {
                    "datetime": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                    "size": size,
                    **error_rate,
                    **result.pop("benchmark"),
                }
            )

            pprint(result)

            data = data.append(result, ignore_index=True)

            if output != "none":
                data.to_csv(output_path)

    return data


def read_csv(file: str) -> pd.DataFrame:
    """Reads a CSV file parses it as a Pandas DataFrame."""
    file_path = Path(file)
    if file_path.exists():
        data = pd.read_csv(file_path, index_col=0)
    else:
        raise FileNotFoundError
    return data


@dataclass
class ThresholdFit:
    """Fitter for code threshold with data obtained by ``~.threshold.run``.
    
    Threshold fitting is performed using the equations described in [wang2003confinement]_. The threshold is computing the ground state of the Hamiltonian that described the phase transition or the Nishimori line in the Random Bond Ising Model. The source provides two functions which are included in this fitting class, where the ``modified_ansatz`` includes a nonuniversion additive correction to correct for finite size effects. 

    .. [wang2003confinement] Chenyang Wang, Jim Harrington and John Preskill, *Confinement-Higgs transition in a disordered gauge theory and the accuracy threshold for quantum memory*, Annals of Physics, 1:31-58, 2003. 
    
    """

    modified_ansatz: bool = False
    p: fit_param = (0.09, 0.1, 0.11)
    A: fit_param = (-np.inf, 0, np.inf)
    B: fit_param = (-np.inf, 0, np.inf)
    C: fit_param = (-np.inf, 0, np.inf)
    D: fit_param = (-2, 1.6, 2)
    nu: fit_param = (0.8, 0.95, 1.2)
    mu: fit_param = (0, 0.7, 3)

    def _get_param(self, i: int) -> tuple:
        return (self.p[i], self.A[i], self.B[i], self.C[i], self.D[i], self.nu[i], self.mu[i])

    def _get_fitting_function(self):
        """Returns the fitting function of curve fitting."""

        def fit(PL, pth, A, B, C, D, nu, mu):
            p, L = PL
            x = (p - pth) * L ** (1 / nu)
            return A + B * x + C * x ** 2

        def fit_modified(PL, pth, A, B, C, D, nu, mu):
            p, L = PL
            x = (p - pth) * L ** (1 / nu)
            return A + B * x + C * x ** 2 + D * L ** (-1 / mu)

        return fit_modified if self.modified_ansatz else fit

    def _get_modified_data(self):
        """Returns the function to obtain data in the rescaled axis."""

        def func(L, x, y, pth, A, B, C, D, nu, mu):
            modified_x = (x - pth) * L ** (1 / nu)
            return modified_x, y

        def func_modified(L, x, y, pth, A, B, C, D, nu, mu):
            modified_x = (x - pth) * L ** (1 / nu)
            modified_y = y - D * L ** (-1 / mu)
            return modified_x, modified_y

        return func_modified if self.modified_ansatz else func

    def fit_data(self, data: pd.DataFrame, column: str, **kwargs):
        """Fits for the code threshold.

        Parameters
        ----------
        data
            Data obtained via `~.threshold.run`.
        column
            The column of the DataFrame to fit for.
        kwargs
            Keyword arguments are passed on the ``scipy.curve_fit``.
        """
        sizes = sorted(list(set(data["size"])))
        rates = sorted(list(set(data[column])))

        simple_data = []
        for size in sizes:
            for rate in rates:
                iters, no_error = 0, 0
                for _, row in data.loc[(data["size"] == size) & (data[column] == rate)].iterrows():
                    iters += row["iterations"]
                    no_error += row["no_error"]
                simple_data.append([size, rate, iters, no_error / iters])

        sizes, rates, iterations, error_rate = tuple(map(list, zip(*simple_data)))

        parameters, covariance = optimize.curve_fit(
            self._get_fitting_function(),
            (rates, sizes),
            error_rate,
            self._get_param(1),
            bounds=[self._get_param(0), self._get_param(2)],
            sigma=[max(iterations) / iters for iters in iterations],
            **kwargs,
        )
        error = np.sqrt(np.diag(covariance))
        print(f"Fitted threshold at {parameters[0]}+-{error[0]}")

        return list(parameters)

    def plot_data(
        self,
        data: pd.DataFrame,
        column: str,
        figure: Figure = None,
        rescaled: bool = False,
        scatter_kwargs: dict = {"s": 10},
        line_kwargs: dict = {"lw": 1.5, "ls": "dashed", "alpha": 0.5},
        axis_attributes: dict = {
            "title": "Threshold",
            "xlabel": "Physical error rate",
            "ylabel": "Logical error rate",
        },
        num_x_fit: int = 1000,
        **kwargs,
    ):
        """Plots the inputted data and the fit for the code threshold.

        Parameters
        ----------
        data
            Data obtained via `~.threshold.run`.
        column
            The column of the DataFrame to fit for.
        figure
            If a figure is attached, `~matplotlib.pyplot.show` is not called. Instead, the figure is returned for futher manipulation.
        rescaled
            Plots the data on a rescaled x axis where the fit is a single line.
        scatter_kwargs
            Keyword arguments to pass on to the `~matplotlib.pyplot.scatter` for the markers.
        line_kwargs
            Keyword arguments to pass on to the ~matplotlib.pyplot.plot for the line plot.
        axis_attributes
            Attributes to set of the axis via ``axis.set_{attribute}(value)``.
        num_x_fit
            Numpy of points to plot for the fit.
        """
        max_iterations = max(data["iterations"])
        data["scatter_size"] = scatter_kwargs.pop("s", 10) * data["iterations"] / max_iterations

        parameters = self.fit_data(data, column)
        fit_func = self._get_fitting_function()

        if not figure:
            figure, axis = plt.subplots()
            show = True
        else:
            axis = plt.gca()
            show = False

        sizes = sorted(list(set(data["size"])))

        colors = [f"C{i%10}" for i, size in enumerate(sizes)]
        markers = [plt_markers[i % len(plt_markers)] for i, size in enumerate(sizes)]
        legend_items = []

        for size, color, marker in zip(sizes, colors, markers):

            size_data = data.loc[data["size"] == size]

            x_data = size_data[column]
            y_data = size_data["no_error"] / size_data["iterations"]
            s_data = size_data["scatter_size"]
            fit_x_data = np.linspace(min(x_data), max(x_data), num_x_fit)
            fit_y_data = [fit_func((x, size), *parameters) for x in fit_x_data]

            if rescaled:
                modifier = self._get_modified_data()
                x_data, y_data = modifier(size, x_data, y_data, *parameters)
                fit_x_data, fit_y_data = modifier(size, fit_x_data, fit_y_data, *parameters)

            axis.scatter(x_data, y_data, s=s_data, color=color, marker=marker, **scatter_kwargs)
            axis.plot(fit_x_data, fit_y_data, color=color, **line_kwargs)

            legend_items.append(Line2D([], [], label=f"L = {size}", color=color, marker=marker, **line_kwargs))

        for attribute, value in axis_attributes.items():
            getattr(axis, f"set_{attribute}")(value)

        axis.legend(handles=legend_items, loc="lower left", ncol=2)

        if show:
            plt.show()
        else:
            return figure
