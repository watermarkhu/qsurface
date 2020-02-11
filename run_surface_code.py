from progiter import ProgIter
import multiprocessing as mp
from decimal import Decimal as dec
import random
import time


def init_random_seed(timestamp=None, worker=0, iteration=0, **kwargs):
    if timestamp is None:
        timestamp = time.time()
    seed = "{:.0f}".format(timestamp*10**7) + str(worker) + str(iteration)
    random.seed(dec(seed))
    return seed


def apply_random_seed(seed=None, **kwargs):
    if seed is None:
        seed = init_random_seed()
    if type(seed) is not dec:
        seed = dec(seed)
    random.seed(seed)


def lattice_type(type, config, dec, go, size):
    if type == "toric":
        decoder = dec.toric(**config.decoder, plot_config=config.plot)
        graph = go.toric(size, decoder, config.plotting, config.plot)
    elif type == "planar":
        decoder = dec.planar(**config.decoder, plot_config=config.plot)
        graph = go.planar(size, decoder, config.plotting, config.plot)
    return decoder, graph


def single(
    config,
    dec,
    go,
    ltype="toric",
    size=10,
    pX=0,
    pZ=0,
    pE=0,
    pmX=0,
    pmZ=0,
    graph=None,
    worker=0,
    iter=0,
    seed=None,
    **kwargs
):
    """
    Runs the peeling decoder for one iteration
    """
    # Initialize lattice
    if graph is None:
        decoder, graph = lattice_type(ltype, config, dec, go, size)

    # Initialize errors
    if seed is None and config.seed is None:
        init_random_seed(worker=worker, iteration=iter)
    elif seed is None:
        apply_random_seed(config.seed)
    elif config.seed is None:
        apply_random_seed(seed)

    graph.apply_and_measure_errors(pX=pX, pZ=pZ, pE=pE, pmX=pmX, pmZ=pmZ)

    # Peeling decoder
    graph.decoder.decode()

    # Measure logical operator
    logical_error, correct = graph.logical_error()
    graph.reset()

    return correct


def multiple(
    iters,
    config,
    dec,
    go,
    ltype="toric",
    size=10,
    pX=0,
    pZ=0,
    pE=0,
    pmX=0,
    pmZ=0,
    qres=None,
    worker=0,
    seeds=None,
    **kwargs
):
    """
    Runs the peeling decoder for a number of iterations. The graph is reused for speedup.
    """

    if seeds is None:
        seeds = [init_random_seed(worker=worker, iteration=iter) for iter in range(iters)]

    decoder, graph = lattice_type(ltype, config, dec, go, size)

    result = [
        single(config, dec, go, ltype, size, pX, pZ, pE, pmX, pmZ ,graph, worker, iter, seed)
        for iter, seed in zip(ProgIter(range(iters)), seeds)
    ]

    N_succes = sum(result)
    if qres is not None:
        qres.put(N_succes)
    else:
        return N_succes


def multiprocess(
        iters,
        config,
        dec,
        go,
        seeds,
        processes,
        **kwargs
        # size, config, dec, iters, pE=0, pX=0, pZ=0, pM=0, seeds=None, processes=None, **kwargs):
    ):
    """
    Runs the peeling decoder for a number of iterations, split over a number of processes
    """

    if processes is None:
        processes = mp.cpu_count()

    # Calculate iterations for ieach child process
    process_iters = iters // processes
    rest_iters = iters - process_iters * (processes - 1)

    # Generate seeds for simulations
    if seeds is None:
        num_seeds = [process_iters for _ in range(processes - 1)] + [rest_iters]
        seed_lists = [[init_random_seed(worker=worker, iteration=iter) for iter in range(iters)] for worker, iters in enumerate(num_seeds)]
    else:
        seed_lists = [seeds[int(i*process_iters):int((i+1)*process_iters)] for i in range(processes - 1)] + [seeds[int((processes-1)*process_iters):]]

    # Initiate processes
    qres = mp.Queue()
    workers = []
    for i in range(processes):
        workers.append(
            mp.Process(
                target=multiple,
                args=(process_iters, config, dec, go),
                kwargs={"qres": qres, "worker": i, "seeds": seed_lists[i], **kwargs},
            )
        )
    print("Starting", processes, "workers.")

    # Start and join processes
    for worker in workers:
        worker.start()

    N_succes = sum([qres.get() for worker in workers])

    for worker in workers:
        worker.join()

    return N_succes


class decoder_config(object):
    def __init__(self):

        self.plotting = 1
        self.seed = None

        self.decoder = {
            "random_order"  : 0,
            "random_traverse":0,
            "print_steps"   : 0,
            "plot_find"     : 1,
            "plot_growth"   : 1,
            "plot_peel"     : 1,
            "plot_nodes"    : 1,
        }

        self.file = {
            "savefile": 0,
            "erasure_file": None,
            "pauli_file": None,
        }

        self.plot = {
            "plot_size"     : 6,
            "line_width"    : 1.5,
            "plotstep_click": 1,
        }


if __name__ == "__main__":

    import unionfind_evengrow_integrated as decoder
    import graph_3D as go

    sim_config = {
        "ltype" : "planar",
        "size"  : 4,
        "pX"    : 0.1,
        "pZ"    : 0.0,
        "pE"    : 0.0,
        "pmX"   : 0.1,
        "pmZ"   : 0.0,
    }
    iters = 50000

    output = single(decoder_config(), decoder, go, **sim_config)

    print(output, output/iters)
