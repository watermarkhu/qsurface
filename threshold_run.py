'''
2020 Mark Shui Hu, QuTech

www.github.com/watermarkhu/oop_surface_code
_____________________________________________

'''
from oopsc import multiple, multiprocess, default_config
from threshold_plot import plot_thresholds
from threshold_fit import fit_data
from pprint import pprint
import numpy as np
import pandas as pd
import git, sys, os


def run_thresholds(
        decoder,
        lattice_type="toric",
        lattices = [],
        perror = [],
        iters = 0,
        measurement_error=False,
        multithreading=False,
        threads=None,
        modified_ansatz=False,
        save_result=True,
        file_name="thres",
        show_plot=False,
        plot_title=None,
        folder = "./",
        P_store=1000,
        debug=False,
        **kwargs
        ):
    '''
    ############################################
    '''
    run_oopsc = multiprocess if multithreading else multiple

    if measurement_error:
        import graph_3D as go
    else:
        import graph_2D as go

    sys.setrecursionlimit(100000)
    r = git.Repo(os.path.dirname(__file__))
    full_name = r.git.rev_parse(r.head, short=True) + f"_{lattice_type}_{go.__name__}_{decoder.__name__}_{file_name}"
    if not plot_title:
        plot_title = full_name

    if not os.path.exists(folder):
        os.makedirs(folder + "/data/", exist_ok=True)
        os.makedirs(folder + "/figures/", exist_ok=True)

    file_path = folder + "/data/" + full_name + ".csv"
    fig_path = folder + "/figures/" + full_name + ".pdf"

    data = None
    int_P = [int(p*P_store) for p in perror]

    # Simulate and save results to file
    for lati in lattices:
        for pi, int_p in zip(perror, int_P):

            print("Calculating for L = ", str(lati), "and p =", str(pi))

            oopsc_args = dict(paulix=pi, lattice_type=lattice_type, debug=debug, processes=threads)
            if measurement_error:
                oopsc_args.update(measurex=pi)
            output = run_oopsc(lati, decoder, go, default_config(**kwargs), iters, **oopsc_args)

            pprint(dict(output))
            print("")

            if data is None:
                if os.path.exists(file_path):
                    data = pd.read_csv(file_path, header=0)
                    data = data.set_index(["L", "p"])
                else:
                    columns = list(output.keys())
                    index = pd.MultiIndex.from_product([lattices, int_P], names=["L", "p"])
                    data = pd.DataFrame(
                        np.zeros((len(lattices) * len(perror), len(columns))), index=index, columns=columns
                    )

            if data.index.isin([(lati, int_p)]).any():
                for key, value in output.items():
                    data.loc[(lati, int_p), key] += value
            else:
                for key, value in output.items():
                    data.loc[(lati, int_p), key] = value

            data = data.sort_index()
            if save_result:
                data.to_csv(file_path)

    print(data.to_string())

    par = fit_data(data, modified_ansatz)

    if show_plot:
        plot_thresholds(data, file_name, fig_path, modified_ansatz, save_result=save_result, par=par)

    if save_result:
        data.to_csv(file_path)


if __name__ == "__main__":

    import argparse
    from oopsc import add_args

    parser = argparse.ArgumentParser(
        prog="threshold_run",
        description="run a threshold computation",
        usage='%(prog)s [-h/--help] decoder lattice_type iters -l [..] -p [..] (lattice_size)'
    )

    parser.add_argument("decoder",
        action="store",
        type=str,
        help="type of decoder - {mwpm/uf/eg}",
        metavar="d",
    )

    parser.add_argument("lattice_type",
        action="store",
        type=str,
        help="type of lattice - {toric/planar}",
        metavar="lt",
    )

    parser.add_argument("iters",
        action="store",
        type=int,
        help="number of iterations - int",
        metavar="i",
    )

    key_arguments = [
        ["-l", "--lattices", "store", "lattice sizes - verbose list int", dict(type=int, nargs='*', metavar="", required=True)],
        ["-p", "--perror", "store", "error rates - verbose list float", dict(type=float, nargs='*', metavar="", required=True)],
        ["-me", "--measurement_error", "store_true", "enable measurement error (2+1D) - toggle", dict()],
        ["-mt", "--multithreading", "store_true", "use multithreading - toggle", dict()],
        ["-nt", "--threads", "store", "number of threads", dict(type=int, metavar="")],

        ["-ma", "--modified_ansatz", "store_true", "use modified ansatz - toggle", dict()],
        ["-s", "--save_result", "store_true", "save results - toggle", dict()],
        ["-sp", "--show_plot", "store_true", "show plot - toggle", dict()],
        ["-fn", "--file_name", "store", "plot filename - toggle", dict(default="thres", metavar="")],
        ["-pt", "--plot_title", "store", "plot filename - toggle", dict(default="", metavar="")],
        ["-f", "--folder", "store", "base folder path - toggle", dict(default="./", metavar="")],
        ["-dgc", "--dg_connections", "store_true", "use dg_connections pre-union processing - toggle", dict()],
        ["-dg", "--directed_graph", "store_true", "use directed graph for evengrow - toggle", dict()],
        ["-db", "--debug", "store_true", "enable debugging hearistics - toggle", dict()]
    ]

    add_args(parser, key_arguments)

    args=vars(parser.parse_args())
    decoder = args.pop("decoder")


    if decoder == "mwpm":
        import mwpm as decode
        print(f"{'_'*75}\n\ndecoder type: minimum weight perfect matching (blossom5)")
    elif decoder == "uf":
        import unionfind as decode
        print(f"{'_'*75}\n\ndecoder type: unionfind")
        if args["dg_connections"]:
            print(f"{'_'*75}\n\nusing dg_connections pre-union processing")
    elif decoder == "eg":
        import unionfind_eg as decode
        print("{}\n\ndecoder type: unionfind evengrow with {} graph".format("_"*75,"directed" if args["directed_graph"] else "undirected"))
        if args["dg_connections"]:
            print(f"{'_'*75}\n\nusing dg_connections pre-union processing")

    run_thresholds(decode, **args)
