import graph_objects as go
import toric_code as tc
import toric_error as te
import toric_plot as tp
import uf_plot as up
import os
from progiter import ProgIter
import multiprocessing as mp


class decoder_config(object):
    def __init__(self, path="./unionfind.ini"):

        if not os.path.exists("./errors/"):
            os.makedirs("./errors/")
        if not os.path.exists("./figures/"):
            os.makedirs("./figures/")

        self.decoder = {
            "print_steps": False,
            "random_order=0": False,
            "random_traverse": False,
            "plot_growth": False,

            # Tree-method
            "intervention": False,
            "vcomb": False,

            # Evengrow
            "plot_nodes": 0,
            "print_nodetree": 0,
        }

        self.file = {
            "savefile": 0,
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
    uf=None,
    config=None,
    **kwargs
):
    """
    Runs the peeling decoder for one iteration
    """
    # import decoder
    if uf is None:
        import unionfind as uf

    # import uf config
    if config is None:
        config = decoder_config()

    # Initialize lattice
    if graph is None:
        graph = go.init_toric_graph(size)

    toric_plot = tp.lattice_plot(graph, **config.plot) if plot_load else None

    # Initialize errors
    if seed is None:
        te.init_random_seed(worker=worker, iteration=iter)

    if pE != 0:
        te.init_erasure_region(graph, pE, toric_plot, **config.file)
        # te.init_erasure(graph, pE, savefile, erasure_file, toric_plot=toric_plot, worker=worker)

    te.init_pauli(graph, pX, pZ, toric_plot, **config.file)

    # Measure stabiliziers
    tc.measure_stab(graph, toric_plot)

    # Peeling decoder
    uf_plot = up.toric(graph, **config.plot)if plot_load else None

    ufg = uf.cluster_farmer(graph, uf_plot, **config.decoder)
    ufg.find_clusters(plot_step=0)
    ufg.grow_clusters()
    ufg.peel_clusters(plot_step=0)

    if toric_plot:
        toric_plot.plot_final()

    # Measure logical operator
    logical_error = tc.logical_error(graph)
    graph.reset()
    correct = True if logical_error == [False, False, False, False] else False

    return correct


def multiple(
    size,
    iters,
    pE=0,
    pX=0,
    pZ=0,
    plot_load=0,
    qres=None,
    worker=0,
    seeds=None,
    uf=None,
    config=None,
    **kwargs
):
    """
    Runs the peeling decoder for a number of iterations. The graph is reused for speedup.
    """
    # import decoder
    if uf is None:
        import unionfind as uf

    # import uf config
    if config is None:
        config = decoder_config()

    if seeds is None:
        seeds = [te.init_random_seed(worker=worker, iteration=iter) for iter in range(iters)]

    graph = go.init_toric_graph(size)

    result = [
        single(size, pE, pX, pZ, plot_load, graph, worker, i, seed, uf, config)
        for i, seed in zip(ProgIter(range(iters)), seeds)
    ]

    N_succes = sum(result)
    if qres is not None:
        qres.put(N_succes)
    else:
        return N_succes


def multiprocess(size, iters, pE=0, pX=0, pZ=0, seeds=None, processes=None, uf=None, config=None, **kwargs):
    """
    Runs the peeling decoder for a number of iterations, split over a number of processes
    """

    # import decoder
    if uf is None:
        import unionfind as uf

    # import uf config
    if config is None:
        config = decoder_config()

    if processes is None:
        processes = mp.cpu_count()

    # Calculate iterations for ieach child process
    process_iters = iters // processes
    rest_iters = iters - process_iters * (processes - 1)

    # Generate seeds for simulations
    if seeds is None:
        num_seeds = [process_iters for _ in range(processes - 1)] + [rest_iters]
        seed_lists = [[te.init_random_seed(worker=worker, iteration=iter) for iter in range(iters)] for worker, iters in enumerate(num_seeds)]
    else:
        seed_lists = [seeds[int(i*process_iters):int((i+1)*process_iters)] for i in range(processes - 1)] + [seeds[int((processes-1)*process_iters):]]

    if uf is None:
        import unionfind as uf

    # Initiate processes
    qres = mp.Queue()
    workers = []
    for i in range(processes - 1):
        workers.append(
            mp.Process(
                target=multiple,
                args=(size, process_iters, pE, pX, pZ, False, qres, i, seed_lists[i], uf, config),
            )
        )
    workers.append(
        mp.Process(
            target=multiple,
            args=(
                size,
                rest_iters,
                pE,
                pX,
                pZ,
                False,
                qres,
                processes - 1,
                seed_lists[processes - 1],
                uf,
                config
            ),
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
