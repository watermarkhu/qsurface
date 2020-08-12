'''
2020 Mark Shui Hu

www.github.com/watermarkhu/OpenSurfaceSim
_____________________________________________

'''
import argparse
from pprint import pprint
from opensurfacesim.main import single, multiple, multiprocess


def add_args(parser, args):
    '''
    helper function to add a list of arguments to a parser object
    '''
    for name, action, type, help, metavar, kwargs in args:
        parser.add_argument(name, action=action, type=type, help=help, metavar=metavar, **kwargs)


def add_kwargs(parser, args, group_name=None, description=None):
    '''
    helper function to add a list of keyword arugments to a parser object
    '''
    if group_name:
        parser = parser.add_argument_group(group_name, description)
    for sid, lid, action, help, kwargs in args:
        parser.add_argument(sid, lid, action=action, help=help, **kwargs)


def proc_kwargs(configuration, arg_group):
    '''
    helper function to extract a list of (keyword) arguments to a dictionary
    '''
    return {arg[1][2:]: configuration.pop(arg[1][2:]) for arg in arg_group}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="Surface code simulation",
        description="simulation of surface code using mwpm/uf/eg decoder",
        usage='%(prog)s [-h/--help] L (lattice_size)'
    )

    arguments = [["lattice_size", "store", int, "size of the lattce", "L", dict()]]

    sim_arguments = [
        ["-i", "--iters", "store", "number of iterations - int", dict(type=int, default=1, metavar="")],
        ["-c", "--code", "store", "type of surface code", dict(type=str, default="toric", metavar="")],
        ["-d", "--decode_module", "store", "type of decoder", dict(type=str, default="uf_bb", metavar="")],
        ["-pm", "--perfect_measurements", "store_true", "force perfect measurements (2D)", dict()],
        ["-s", "--seed", "store", "seeds for the simulations - verbose list", dict(type=int, nargs='*', metavar="")],
        ["-mt", "--multithreading", "store_true", "use multithreading - toggle", dict()],
        ["-nt", "--threads", "store", "number of threads (defaults to available # logical cores) - int", dict(type=int, metavar="")],
        ["-bm", "--benchmark", "store_true", "enable statistics - toggle", dict()]
    ]

    error_arguments = [
        ["-px", "--paulix", "store", "Pauli X error rate - float {0,1}", dict(type=float, default=0, metavar="")],
        ["-pz", "--pauliz", "store", "Pauli Y error rate - float {0,1}", dict(type=float, default=0, metavar="")],
        ["-pmx", "--measurex", "store", "Measurement X error rate - float {0,1}", dict(type=float, default=0, metavar="")],
        ["-pmz", "--measurez", "store", "Measurement Y error rate - float {0,1}", dict(type=float, default=0, metavar="")],
        ["-pe", "--erasure", "store", "Erasure - float {0,1}", dict(type=float, default=0, metavar="")],
    ]

    plot_arguments = [
        ["-p2d", "--plot2D", "store_true", "plot 2D lattice - toggle", dict()],
        ["-p3d", "--plot3D", "store_true", "plot 3D lattice - toggle", dict()],
        ["-puf", "--plotUF", "store_true", "plot uf-lattice - toggle", dict()]
    ]

    add_args(parser, arguments)
    add_kwargs(parser, sim_arguments, "simulation", "arguments for simulation")
    add_kwargs(parser, error_arguments, "errors", "arguments for errors")
    add_kwargs(parser, plot_arguments, "figure", "arguments for plotting")

    configuration = vars(parser.parse_args())
    
    sim_kwargs = proc_kwargs(configuration, sim_arguments)
    error_rates = proc_kwargs(configuration, error_arguments)
    plot_kwargs = proc_kwargs(configuration, plot_arguments)

    size = configuration.pop("lattice_size")
    iters = sim_kwargs.pop("iters")
    multi   = sim_kwargs.pop("multithreading")
    threads = sim_kwargs.pop("threads")

    if iters == 1:
        output = single(size, error_rates=error_rates, plot_kwargs=plot_kwargs, **sim_kwargs)
    elif not multi:
        output = multiple(size, iters, error_rates=error_rates, ** sim_kwargs)
    else:
        output = multiprocess(size, iters, error_rates=error_rates, processes=threads, **sim_kwargs)

    pprint(dict(output=dict(output)))
