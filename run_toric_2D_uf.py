import graph_objects as go
import toric_code as tc
import toric_error as te
import toric_plot as tp
import unionfind_dgclusters as uf
import uf_plot as up
import os
from progiter import ProgIter
import multiprocessing as mp


def single(
    size,
    pE=0,
    pX=0,
    pZ=0,
    method="list",
    savefile=0,
    erasure_file=None,
    pauli_file=None,
    plot_load=False,
    graph=None,
    worker=0,
    iter=0,
):
    """
    Runs the peeling decoder for one iteration
    """

    if not os.path.exists("./errors/"):
        os.makedirs("./errors/")
    if not os.path.exists("./figures/"):
        os.makedirs("./figures/")

    # Initialize lattice
    if graph is None:
        graph = go.init_toric_graph(size)

    toric_plot = (
        tp.lattice_plot(graph, plot_size=8, line_width=2) if plot_load else None
    )


    # Initialize errors
    te.init_random_seed(worker=worker, iteration=iter)
    if pE != 0:
        te.init_erasure_region(
            graph,
            pE,
            savefile,
            erasure_file=erasure_file,
            toric_plot=toric_plot
        )
        # te.init_erasure(graph, pE, savefile, erasure_file, toric_plot=toric_plot, worker=worker)

    te.init_pauli(
        graph,
        pX,
        pZ,
        savefile,
        pauli_file=pauli_file,
        toric_plot=toric_plot,
    )

    # Measure stabiliziers
    tc.measure_stab(graph, toric_plot)

    # Peeling decoder
    uf_plot = (
        up.toric(graph, toric_plot.f, plot_size=8, line_width=1.5, plotstep_click=1)
        if plot_load
        else None
    )

    ufg = uf.cluster_farmer(
        graph,
        uf_plot,
        plot_growth=0,
        print_steps=0,
        random_traverse=0,
        intervention=0,
        vcomb=0
    )
    ufg.find_clusters(plot_step=0)
    ufg.grow_clusters(method)
    ufg.peel_clusters(plot_step=0)

    if toric_plot:
        toric_plot.plot_final()

    # Measure logical operator
    logical_error = tc.logical_error(graph)
    graph.reset()
    correct = True if logical_error == [False, False, False, False] else False
    return correct


def multiple(
    size, iters, pE=0, pX=0, pZ=0, method="list", plot_load=0, qres=None, worker=None
):
    """
    Runs the peeling decoder for a number of iterations. The graph is reused for speedup.
    """
    graph = go.init_toric_graph(size)
    result = [
        single(
            size, pE, pX, pZ, method=method, plot_load=plot_load, graph=graph, worker=worker, iter=i
        )
        for i in ProgIter(range(iters))
    ]
    N_succes = sum(result)
    if qres is not None:
        qres.put(N_succes)
    else:
        return N_succes


def multiprocess(size, iters, pE=0, pX=0, pZ=0, method="list", processes=None):
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
                target=multiple,
                args=(size, process_iters, pE, pX, pZ, method, False, qres, i),
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
                method,
                False,
                qres,
                processes - 1,
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
