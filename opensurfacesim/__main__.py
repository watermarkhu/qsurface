from opensurfacesim.main import BenchmarkDecoder, run, run_multiprocess, initialize
from opensurfacesim.threshold import run_many, ThresholdFit, read_csv
from collections import defaultdict
import argparse
import sys


def _add_kwargs(parser, args, group_name=None, description=None):
    """
    helper function to add a list of keyword arguments to a parser object
    """
    if group_name:
        parser = parser.add_argument_group(group_name, description)
    for sid, lid, action, help_txt, kwargs in args:
        if action == "store_true":
            parser.add_argument(sid, lid, action=action, help=help_txt, **kwargs)
        else:
            parser.add_argument(sid, lid, action=action, help=help_txt, metavar="", **kwargs)


def _get_kwargs(parsed_args, arg_group):
    """
    helper function to extract a list of (keyword) arguments to a dictionary
    """
    return {arg[1][2:]: parsed_args.get(arg[1][2:]) for arg in arg_group}


def cli(args):

    parser = argparse.ArgumentParser(
        prog="opensurfacesim",
        description="Simulation of surface codes. Need more information here",
        usage="%(prog)s",
    )

    subparsers = parser.add_subparsers(help="sub-command help", dest="sub")

    init_arguments = [
        ["-C", "--Code", "store", "type of surface code", dict(type=str, default="toric")],
        ["-D", "--Decoder", "store", "type of decoder", dict(type=str, default="mwpm")],
        [
            "-e",
            "--enabled_errors",
            "store",
            "error modules - verbose list",
            dict(type=str, nargs="*", default=[]),
        ],
        ["-fm", "--faulty_measurements", "store_true", "enable faulty measurements (3D)", dict()],
        ["-p", "--plotting", "store_true", "enable plotting", dict()],
    ]
    _add_kwargs(parser, init_arguments, "initialization", "arguments for simulation initialization")
    benchmark_arguments = [
        [
            "-du",
            "--duration",
            "store",
            "get durations - verbose list",
            dict(type=str, nargs="*", default=[]),
        ],
        [
            "-vl",
            "--value_to_list",
            "store",
            "count_calls - verbose list",
            dict(type=str, nargs="*", default=[]),
        ],
        [
            "-cc",
            "--count_calls",
            "store",
            "count_calls - verbose list",
            dict(type=str, nargs="*", default=[]),
        ],
    ]

    ### Simulation

    simulation_parser = subparsers.add_parser("simulation", help="run the simulation")
    sim_arguments = [
        ["-l", "--size", "store", "size - int", dict(type=int, default=3)],
        ["-n", "--iterations", "store", "number of iterations - int", dict(type=int, default=1)],
        [
            "-s",
            "--seed",
            "store",
            "seed for the simulations - verbose list",
            dict(type=int, nargs="*"),
        ],
        [
            "-mp",
            "--processes",
            "store",
            "number of threads (defaults to available # logical cores) - int",
            dict(type=int, default=1),
        ],
    ]
    error_arguments = [
        ["-px", "--p_bitflip", "store", "Bitflip rate - float {0,1}", dict(type=float, default=0)],
        [
            "-pz",
            "--p_phaseflip",
            "store",
            "Phaseflip rate - float {0,1}",
            dict(type=float, default=0),
        ],
        ["-pe", "--p_erasure", "store", "Erasure rate - float {0,1}", dict(type=float, default=0)],
        [
            "-pmx",
            "--p_bitflip_plaq",
            "store",
            "Measurement bitflip rate - float {0,1}",
            dict(type=float, default=0),
        ],
        [
            "-pmz",
            "--p_bitflip_star",
            "store",
            "Measurement phaseflip rate - float {0,1}",
            dict(type=float, default=0),
        ],
    ]
    _add_kwargs(simulation_parser, sim_arguments, "simulation", "arguments for simulation")
    _add_kwargs(simulation_parser, error_arguments, "errors", "arguments for errors")

    sim_sub_parsers = simulation_parser.add_subparsers(help="sub-command help", dest="simulation_sub")
    sim_bench_parser = sim_sub_parsers.add_parser("benchmark", help="do benchmark")
    benchmark_arguments = [
        [
            "-du",
            "--duration",
            "store",
            "get durations - verbose list",
            dict(type=str, nargs="*", default=[]),
        ],
        [
            "-vl",
            "--value_to_list",
            "store",
            "count_calls - verbose list",
            dict(type=str, nargs="*", default=[]),
        ],
        [
            "-cc",
            "--count_calls",
            "store",
            "count_calls - verbose list",
            dict(type=str, nargs="*", default=[]),
        ],
    ]
    _add_kwargs(sim_bench_parser, benchmark_arguments)

    ### Threshold

    threshold_parser = subparsers.add_parser("threshold", help="run threshold simulation")
    thres_arguments = [
        ["-l", "--sizes", "store", "sizes of suraces", dict(type=int, default=3, nargs="*")],
        [
            "-n",
            "--iterations",
            "store",
            "number of iterations per configuration",
            dict(type=int, default=1),
        ],
        [
            "-mp",
            "--mp_processes",
            "store",
            "number of multiprocessing threads",
            dict(type=int, default=1),
        ],
        ["-fc", "--fit_column", "store", "fit threshold of column", dict(type=str)],
        ["-pc", "--plot_column", "store", "plot threshold of column", dict(type=str)],
        [
            "-o",
            "--output",
            "store",
            "output file name, (none) for no output",
            dict(type=str, default=""),
        ],
        [
            "-i",
            "--input",
            "store",
            "input file name, use with -fc or -pc to fit and flot existing data",
            dict(type=str, default=""),
        ],
    ]
    thres_error_arguments = [
        ["-px", "--p_bitflip", "store", "Bitflip rate - float {0,1}", dict(type=float, nargs="*")],
        [
            "-pz",
            "--p_phaseflip",
            "store",
            "Phaseflip rate - float {0,1}",
            dict(type=float, nargs="*"),
        ],
        ["-pe", "--p_erasure", "store", "Erasure rate - float {0,1}", dict(type=float, nargs="*")],
        [
            "-pmx",
            "--p_bitflip_plaq",
            "store",
            "Measurement bitflip rate - float {0,1}",
            dict(type=float, nargs="*"),
        ],
        [
            "-pmz",
            "--p_bitflip_star",
            "store",
            "Measurement phaseflip rate - float {0,1}",
            dict(type=float, nargs="*"),
        ],
    ]
    _add_kwargs(threshold_parser, thres_arguments, "simulation", "arguments for simulation")
    _add_kwargs(threshold_parser, thres_error_arguments, "errors", "arguments for errors")
    thres_sub_parsers = threshold_parser.add_subparsers(help="sub-command help", dest="threshold_sub")
    thres_bench_parser = thres_sub_parsers.add_parser("benchmark", help="do benchmark")
    _add_kwargs(thres_bench_parser, benchmark_arguments)

    ###

    parsed_args = vars(parser.parse_args(args))
    init_kwargs = _get_kwargs(parsed_args, init_arguments)

    if parsed_args["sub"] == "simulation":

        error_rates = _get_kwargs(parsed_args, error_arguments)
        sim_kwargs = _get_kwargs(parsed_args, sim_arguments)

        if parsed_args["simulation_sub"] == "benchmark":
            bench_kwargs = _get_kwargs(parsed_args, benchmark_arguments)
            methods_to_benchmark = defaultdict(list)
            for decorator, decorated in bench_kwargs.items():
                for function in decorated:
                    methods_to_benchmark[function].append(decorator)
            benchmark = BenchmarkDecoder(methods_to_benchmark, seed=sim_kwargs["seed"])
        else:
            benchmark = None

        code, decoder = initialize(sim_kwargs.pop("size"), **init_kwargs)
        runner = run_multiprocess if sim_kwargs["processes"] > 1 else run
        output = runner(code, decoder, error_rates=error_rates, benchmark=benchmark, **sim_kwargs)
        print(output)

    elif parsed_args["sub"] == "threshold":

        init_kwargs.pop("plotting")
        init_kwargs.update(_get_kwargs(parsed_args, thres_arguments))
        fit_column = init_kwargs.pop("fit_column")
        plot_column = init_kwargs.pop("plot_column")
        file = init_kwargs.pop("input")

        if file:
            data = read_csv(file)
        else:
            error_kwargs = _get_kwargs(parsed_args, thres_error_arguments)
            error_lists = {name: errors for name, errors in error_kwargs.items() if errors}
            try:
                iterated_lists = list(map(list, zip(*error_lists.values())))
            except:
                raise IndexError("Not all errors have the same length.")
            error_rates = [{name: rate for name, rate in zip(error_lists.keys(), rates)} for rates in iterated_lists]

            if parsed_args["threshold_sub"] == "benchmark":
                bench_kwargs = _get_kwargs(parsed_args, benchmark_arguments)
                methods_to_benchmark = defaultdict(list)
                for decorator, decorated in bench_kwargs.items():
                    for function in decorated:
                        methods_to_benchmark[function].append(decorator)
            else:
                methods_to_benchmark = {}

            data = run_many(
                init_kwargs.pop("Code"),
                init_kwargs.pop("Decoder"),
                error_rates=error_rates,
                methods_to_benchmark=methods_to_benchmark,
                **init_kwargs
            )

        print(data)

        if fit_column or plot_column:
            fitter = ThresholdFit()
            if fit_column:
                fitter.fit_data(data, fit_column)
            if plot_column:
                fitter.plot_data(data, plot_column)


if __name__ == "__main__":

    args = sys.argv
    cli(args[1:])
