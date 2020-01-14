import graph_objects as go
import toric_code as tc
import toric_error as te
import toric_plot as tp
from progiter import ProgIter
import multiprocessing as mp
import os

class decoder_config(object):
    def __init__(self, path="./unionfind.ini"):

        if not os.path.exists("./errors/"):
            os.makedirs("./errors/")
        if not os.path.exists("./figures/"):
            os.makedirs("./figures/")

        self.file = {
            "savefile": False,
            "erasure_file": None,
            "pauli_file": None,
        }

        self.plot = {
            "plot_size": 6,
            "line_width": 1.5,
            "plotstep_click": True
        }


def single(
    size,
    pE=0,
    pX=0,
    pZ=0,
    plot_load=False,
    graph=None,
    worker=0,
    iter=0,
    seed=None,
    config=None,
    **kwargs
):
    """
    Runs the peeling decoder for one iteration
    """

    # import uf config
    if config is None:
        config = decoder_config()

    # Initialize lattice
    if graph is None:
        graph = go.init_toric_graph(size)

    toric_plot = tp.lattice_plot(graph, **config.plot) if plot_load else None

    # Initialize errors
    te.init_random_seed(worker=worker, iteration=iter)

    if pE != 0:
        te.init_erasure_region(graph, pE, toric_plot, **config.file)
        # te.init_erasure(graph, pE, savefile, erasure_file, toric_plot=toric_plot, worker=worker)

    te.init_pauli(graph, pX, pZ, toric_plot, **config.file)

    # Measure stabiliziers
    tc.measure_stab(graph, toric_plot)

    # MWPM decoder
    # matching = tc.get_matching_mwpm(graph)
    matching = tc.get_matching_blossom5(graph)

    # Apply matching
    tc.apply_matching_mwpm(graph, matching, toric_plot)

    # Measure logical operator
    logical_error = tc.logical_error(graph)
    graph.reset()
    correct = True if logical_error == [False, False, False, False] else False
    return correct


def multiple(size, iters, pE=0, pX=0, pZ=0, plot_load=False, qres=None, worker=None, seeds=None, config=None, **kwargs):
    """
    Runs the peeling decoder for a number of iterations. The graph is reused for speedup.
    """
    # import uf config
    if config is None:
        config = decoder_config()

    if seeds is None:
        seeds = [te.init_random_seed(worker=worker, iteration=iter) for iter in range(iters)]

    graph = go.init_toric_graph(size)
    result = [
        single(size, pE, pX, pZ, plot_load, graph, worker, i, seed, config)
        for i, seed in ProgIter(zip(range(iters), seeds))
    ]

    N_succes = sum(result)
    if qres is not None:
        qres.put(N_succes)
    else:
        return N_succes


def multiprocess(size, iters, pE=0, pX=0, pZ=0, seeds=None, processes=None, config=None, **kwargs):
    """
    Runs the peeling decoder for a number of iterations, split over a number of processes
    """
    # import uf config
    if config is None:
        config = decoder_config()

    if processes is None:
        processes = mp.cpu_count()

    # Calculate iterations for ieach child process
    process_iters = iters // processes
    rest_iters = iters - process_iters * processes

    # Generate seeds for simulations
    if seeds is None:
        num_seeds = [process_iters for _ in range(processes - 1)] + [rest_iters]
        seed_lists = [[te.init_random_seed(worker=worker, iteration=iter) for iter in range(iters)] for worker, iters in enumerate(num_seeds)]
    else:
        seed_lists = [seeds[int(i*process_iters):int((i+1)*process_iters)] for i in range(processes - 1)] + [seeds[int((processes-1)*process_iters):]]

    # Initiate processes
    qres = mp.Queue()
    workers = []
    for i in range(processes - 1):
        workers.append(
            mp.Process(
                target=multiple, args=(size, process_iters, pE, pX, pZ, False, qres, i, seed_lists[i], config)
            )
        )
    workers.append(
        mp.Process(
            target=multiple,
            args=(
                size,
                process_iters + rest_iters,
                pE,
                pX,
                pZ,
                False,
                qres,
                processes - 1,
                seed_lists[processes - 1],
                config
            ),
        )
    )

    # Start and join processes
    for worker in workers:
        worker.start()
    print("Started", processes, "workers.")
    for worker in workers:
        worker.join()

    results = [qres.get() for worker in workers]
    return sum(results)
