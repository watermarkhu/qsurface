from opensurfacesim.main import BenchmarkDecoder, run, run_multiprocess, initialize
from collections import defaultdict
import argparse

def _add_kwargs(parser, args, group_name=None, description=None):
    '''
    helper function to add a list of keyword arguments to a parser object
    '''
    if group_name:
        parser = parser.add_argument_group(group_name, description)
    for sid, lid, action, help_txt, kwargs in args:
        if action == "store_true":
            parser.add_argument(sid, lid, action=action, help=help_txt, **kwargs)
        else:
            parser.add_argument(sid, lid, action=action, help=help_txt, metavar="", **kwargs)

def _get_kwargs(parsed_args, arg_group):
    '''
    helper function to extract a list of (keyword) arguments to a dictionary
    '''
    return {arg[1][2:]: parsed_args.get(arg[1][2:]) for arg in arg_group}


def cli():

    parser = argparse.ArgumentParser(
        prog="Surface code simulation",
        description="simulation of surface code decoding",
        usage='%(prog)s [-h/--help] L (lattice_size)'
    )

    subparsers = parser.add_subparsers(help='sub-command help', dest="sub") 

    init_arguments = [
        ["-C", "--Code", "store", "type of surface code", dict(type=str, default="toric")],
        ["-D", "--Decoder", "store", "type of decoder", dict(type=str, default="mwpm")],
        ["-e", "--enabled_errors", "store", "error modules - verbose list", dict(type=str, nargs='*', default=[])],
        ["-fm", "--faulty_measurements", "store_true", "enable faulty measurements (3D)", dict()],
        ["-p", "--plotting", "store_true", "enable plotting", dict()],
    ]
    _add_kwargs(parser, init_arguments, "initialization", "arguments for simulation initialization")
    benchmark_arguments = [
        ["-du", "--duration", "store", "get durations - verbose list", dict(type=str, nargs="*", default=[])],
        ["-vl", "--value_to_list", "store", "count_calls - verbose list", dict(type=str, nargs="*", default=[])],
        ["-cc", "--count_calls", "store", "count_calls - verbose list", dict(type=str, nargs="*", default=[])],
    ]

    ### Simulation

    simulation_parser = subparsers.add_parser("simulation",help="run the simulation")
    sim_arguments = [
        ["-l", "--size", "store", "size - int", dict(type=int, default=3)],
        ["-i", "--iterations", "store", "number of iterations - int", dict(type=int, default=1)],
        ["-s", "--seed", "store", "seed for the simulations - verbose list", dict(type=int, nargs='*')],
        ["-mp", "--processes", "store", "number of threads (defaults to available # logical cores) - int", dict(type=int, default=1)],
    ]
    error_arguments = [
        ["-px", "--p_bitflip", "store", "Bitflip rate - float {0,1}", dict(type=float, default=0)],
        ["-pz", "--p_phaseflip", "store", "Phaseflip rate - float {0,1}", dict(type=float, default=0)],
        ["-pe", "--p_erasure", "store", "Erasure rate - float {0,1}", dict(type=float, default=0)],
        ["-pmx", "--pm_bitflip", "store", "Measurement bitflip rate - float {0,1}", dict(type=float, default=0)],
        ["-pmz", "--pm_phaseflip", "store", "Measurement phaseflip rate - float {0,1}", dict(type=float, default=0)],
    ]
    _add_kwargs(simulation_parser, sim_arguments, "simulation", "arguments for simulation")
    _add_kwargs(simulation_parser, error_arguments, "errors", "arguments for errors")

    sim_sub_parsers = simulation_parser.add_subparsers(help='sub-command help', dest="simulation_sub") 
    sim_bench_parser = sim_sub_parsers.add_parser("benchmark",help="do benchmark")
    benchmark_arguments = [
        ["-du", "--duration", "store", "get durations - verbose list", dict(type=str, nargs="*", default=[])],
        ["-vl", "--value_to_list", "store", "count_calls - verbose list", dict(type=str, nargs="*", default=[])],
        ["-cc", "--count_calls", "store", "count_calls - verbose list", dict(type=str, nargs="*", default=[])],
    ]
    _add_kwargs(sim_bench_parser, benchmark_arguments)

    ###

    parsed_args = vars(parser.parse_args())
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

if __name__ == "__main__":
    cli()