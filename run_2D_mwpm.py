import graph_objects as go
import dec_mwpm as dc
import toric_error2 as te
import surface_plot as tp
from progiter import ProgIter
import multiprocessing as mp


def single(
    size,
    pE=0,
    pX=0,
    pZ=0,
    plot_load=False,
    type="toric",
    graph=None,
    worker=0,
    iter=0,
):
    """
    Runs the peeling decoder for one iteration
    """

    # Initialize lattice

    if type == "toric":
        graph = go.init_toric_graph(size)
        decoder = dc.toric(graph)
    elif type == "planar":
        graph = go.init_planar_graph(size)
        decoder = dc.planar(graph)

    if plot_load:
        lplot = tp.lattice_plot(graph, plot_size=8, line_width=2)
        te.init_random_seed(worker=worker, iteration=iter)
        te.init_erasure(graph, pE)
        lplot.plot_erasures()
        te.init_pauli(graph, pX, pZ)
        lplot.plot_errors()
        graph.measure_stab()
        lplot.plot_syndrome()
        decoder.get_matching_blossom5()
        if type == "planar":
            decoder.remove_virtual()
        lplot.plot_lines(decoder.matching)
        decoder.apply_matching()
        lplot.plot_final()

    else:
        te.init_random_seed(worker=worker, iteration=iter)
        te.init_erasure(graph, pE)
        te.init_pauli(graph, pX, pZ)
        graph.measure_stab()
        decoder.get_matching_blossom5()
        if type == "planar":
            decoder.remove_virtual()
        decoder.apply_matching()


    _ , correct = go.logical_error(graph)

    return correct


def multiple(size, iters, pE=0, pX=0, pZ=0, plot_load=False, type="toric", qres=None, worker=0):
    """
    Runs the peeling decoder for a number of iterations. The graph is reused for speedup.
    """
    graph = go.init_toric_graph(size)
    result = [
        single(
            size, pE, pX, pZ, plot_load=plot_load, type=type, graph=graph, worker=worker, iter=i
        )
        for i in ProgIter(range(iters))
    ]
    N_succes = sum(result)
    if qres is not None:
        qres.put(N_succes)
    else:
        return N_succes


def multiprocess(size, iters, pE=0, pX=0, pZ=0, type="toric", processes=None):
    """
    Runs the peeling decoder for a number of iterations, split over a number of processes
    """

    if processes is None:
        processes = mp.cpu_count()

    # Calculate iterations for ieach child process
    process_iters = iters // processes
    rest_iters = iters - process_iters * processes

    # Initiate processes
    qres = mp.Queue()
    workers = []
    for i in range(processes - 1):
        workers.append(
            mp.Process(
                target=multiple, args=(size, process_iters, pE, pX, pZ, False, type, qres, i)
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
                type,
                qres,
                processes - 1,
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
