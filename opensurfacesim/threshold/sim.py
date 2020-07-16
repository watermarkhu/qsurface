'''
2020 Mark Shui Hu

www.github.com/watermarkhu/OpenSurfaceSim
_____________________________________________

'''
from simulator import main, configuration
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
    fitp = data.index.get_level_values("p")
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
        code="toric",
        decode_module="mwpm",
        lattices=[],
        perror = [],
        iters = 0,
        perfect_measurements=False,
        multithreading=False,
        threads=None,
        output="",
        folder = ".",
        **kwargs
        ):
    '''
    ############################################
    '''
    run_sim = main.multiprocess if multithreading else main.multiple
    sys.setrecursionlimit(100000)

    config = dict(**kwargs)
    graph = configuration.setup_decoder(code, decode_module, 3, perfect_measurements)

    full_name = f"{code}_{str(graph).split()[0]}_{decode_module}_{output}"

    if not os.path.exists(folder):
        os.makedirs(folder)
    file_path = folder + "/" + full_name + ".csv"

    data = None
    pfloat = [float(p) for p in perror]
    pstr = [str(p) for p in perror]

    # Simulate and save results to file
    for lati in lattices:

        if multithreading:
            if threads is None:
                threads = mp.cpu_count()
            decoder = [configuration.setup_decoder(code, decode_module, lati, perfect_measurements, info=0) for _ in range(threads)]
        else:
            decoder = configuration.setup_decoder(code, decode_module, lati, perfect_measurements, info=0)

        for spi, fpi in zip(pstr, pfloat):

            print("Calculating for L = ", str(lati), "and p =", spi)

            error_rates = dict(paulix=fpi)
            if not perfect_measurements:
                error_rates.update(measurex=fpi)
            result = run_sim(lati, iters, decoder=decoder, error_rates=error_rates, **kwargs)

            pprint(dict(result))
            print("")

            if data is None:
                if os.path.exists(file_path):
                    data = pd.read_csv(file_path, header=0)
                    data = data.set_index(["L", "p"])
                else:
                    columns = list(result.keys())
                    index = pd.MultiIndex.from_product([lattices, pstr], names=["L", "p"])
                    data = pd.DataFrame(
                        np.zeros((len(lattices) * len(perror), len(columns))), index=index, columns=columns
                    )

            if data.index.isin([(lati, spi)]).any():
                for key, value in result.items():
                    data.loc[(lati, spi), key] += value
            else:
                for key, value in result.items():
                    data.loc[(lati, spi), key] = value

            data = data.sort_index()
            if output:
                data.to_csv(file_path)

    print(data.to_string())

    if output:
        print("file saved to {}".format(file_path))
        data.to_csv(file_path)
