'''
2020 Mark Shui Hu

www.github.com/watermarkhu/OpenSurfaceSim
_____________________________________________

'''
from .. import main
from pprint import pprint
import multiprocessing as mp
import numpy as np
import pandas as pd
import sys, os


def read_data(file_path):
    try:
        data = pd.read_csv(file_path, header=0)
        return data.set_index(["L", "p"])
    except FileNotFoundError:
        print("File not found")
        exit()


def get_data(data, latts, probs):

    if not latts: latts = []
    if not probs: probs = []
    fitL = data.index.get_level_values("L")
    fitp = [round(p, 8) for p in data.index.get_level_values("p")]
    fitN = data.loc[:, "N"].values
    fitt = data.loc[:, "succes"].values

    fitdata = [[] for i in range(4)]
    for L, p, N, t in zip(fitL, fitp, fitN, fitt):
        if all([N != 0, not latts or L in latts, not probs or p in probs]):
            fitdata[0].append(L)
            fitdata[1].append(p)
            fitdata[2].append(N)
            fitdata[3].append(t)

    return fitdata[0], fitdata[1], fitdata[2], fitdata[3]


def sim_thresholds(
        decoder,
        lattice_type="toric",
        lattices = [],
        perror = [],
        iters = 0,
        measurement_error=False,
        multithreading=False,
        threads=None,
        output="",
        folder = ".",
        debug=False,
        **kwargs
        ):
    '''
    ############################################
    '''
    run_oopsc = main.multiprocess if multithreading else main.multiple

    if measurement_error:
        from ..graph import graph_3D as go
    else:
        from ..graph import graph_2D as go

    sys.setrecursionlimit(100000)

    get_name = lambda s: s[s.rfind(".")+1:]
    g_type = get_name(go.__name__)
    d_type = get_name(decoder.__name__)
    full_name = f"{lattice_type}_{g_type}_{d_type}_{output}"

    if not os.path.exists(folder):
        os.makedirs(folder)
    file_path = folder + "/" + full_name + ".csv"

    progressbar = kwargs.pop("progressbar")

    data = None
    pfloat = [float(p) for p in perror]
    config = main.default_config(**kwargs)

    # Simulate and save results to file
    for lati in lattices:

        if multithreading:
            if threads is None:
                threads = mp.cpu_count()
            graph = [main.lattice_type(lattice_type, config, decoder, go, lati) for _ in range(threads)]
        else:
            graph = main.lattice_type(lattice_type, config, decoder, go, lati)

        for pi, fpi in zip(perror, pfloat):

            print("Calculating for L = ", str(lati), "and p =", str(pi))

            oopsc_args = dict(
                paulix=fpi,
                lattice_type=lattice_type,
                debug=debug,
                processes=threads,
                progressbar=progressbar
            )
            if measurement_error:
                oopsc_args.update(measurex=fpi)
            output = run_oopsc(lati, config, iters, graph=graph, **oopsc_args)

            pprint(dict(output))
            print("")

            if data is None:
                if os.path.exists(file_path):
                    data = pd.read_csv(file_path, header=0)
                    data = data.set_index(["L", "p"])
                else:
                    columns = list(output.keys())
                    index = pd.MultiIndex.from_product([lattices, perror], names=["L", "p"])
                    data = pd.DataFrame(
                        np.zeros((len(lattices) * len(perror), len(columns))), index=index, columns=columns
                    )


            if data.index.isin([(lati, fpi)]).any():
                for key, value in output.items():
                    data.loc[(lati, fpi), key] += value
            else:
                for key, value in output.items():
                    data.loc[(lati, fpi), key] = value

            data = data.sort_index()
            if output:
                data.to_csv(file_path)

    print(data.to_string())

    if output:
        print("file saved to {}".format(file_path))
        data.to_csv(file_path)
