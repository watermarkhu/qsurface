'''
2020 Mark Shui Hu

www.github.com/watermarkhu/OpenSurfaceSim
_____________________________________________

'''
import argparse
from pprint import pprint
from simulator.main import single, multiple, multiprocess


def add_args(parser, args):
    for name, action, type, help, metavar, kwargs in args:
        parser.add_argument(name, action=action, type=type, help=help, metavar=metavar, **kwargs)


def add_kwargs(parser, args, group_name=None, description=None):

    if group_name:
        parser = parser.add_argument_group(group_name, description)
    for sid, lid, action, help, kwargs in args:
        parser.add_argument(sid, lid, action=action, help=help, **kwargs)


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
        ["-d", "--decoder", "store", "type of decoder", dict(type=str, default="uf_bb", metavar="")],
        ["-px", "--paulix", "store", "Pauli X error rate - float {0,1}", dict(type=float, default=0, metavar="")],
        ["-pz", "--pauliz", "store", "Pauli Y error rate - float {0,1}", dict(type=float, default=0, metavar="")],
        ["-pmx", "--measurex", "store", "Measurement X error rate - float {0,1}", dict(type=float, default=0, metavar="")],
        ["-pmz", "--measurez", "store", "Measurement Y error rate - float {0,1}", dict(type=float, default=0, metavar="")],
        ["-pe", "--erasure", "store", "Erasure - float {0,1}", dict(type=float, default=0, metavar="")],
        ["-s", "--seeds", "store", "seeds for the simulations - verbose list", dict(type=int, nargs='*', metavar="")],
        ["-mt", "--multithreading", "store_true", "use multithreading - toggle", dict()],
        ["-nt", "--threads", "store", "number of threads (defaults to available # logical cores) - int", dict(type=int, metavar="")],
        ["-f2d", "--force2D", "store_true", "force 2D lattice - toggle", dict()],
        ["-f3d", "--force3D", "store_true", "force 3D lattice - toggle", dict()],
        ["-db", "--debug", "store_true", "enable debugging hearistics - toggle", dict()]
    ]

    plot_arguments = [
        ["-p2d", "--plot2D", "store_true", "plot 2D lattice - toggle", dict()],
        ["-p3d", "--plot3D", "store_true", "plot 3D lattice - toggle", dict()],
        ["-puf", "--plotUF", "store_true", "plot uf-lattice - toggle", dict()]
    ]

    add_args(parser, arguments)
    add_kwargs(parser, sim_arguments, "simulation", "arguments for simulation")
    add_kwargs(parser, plot_arguments, "figure", "arguments for plotting")


    config=vars(parser.parse_args())
    decoder = config.pop("decoder")
    iters   = config.pop("iters")
    multi   = config.pop("multithreading")
    threads = config.pop("threads")
    size    = config.pop("lattice_size")
    debug   = config.pop("debug")

    kwargs = dict(
        code        = config.pop("code"),
        paulix      = config.pop("paulix"),
        pauliz      = config.pop("pauliz"),
        erasure     = config.pop("erasure"),
        measurex    = config.pop("measurex"),
        measurez    = config.pop("measurez"),
        f2d         = config.pop("force2D"),
        f3d         = config.pop("force3D")
    )

    if iters == 1:
        output = single(size, config, decoder=decoder, debug=debug, **kwargs)
    elif not multi:
        output = multiple(size, config, iters, decoder=decoder, debug=debug, **kwargs)
    else:
        output = multiprocess(size, config, iters, decoder=decoder, debug=debug, processes=threads, **kwargs)

    pprint(output)
