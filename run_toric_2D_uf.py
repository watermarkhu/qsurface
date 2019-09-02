import graph_objects as go
import toric_code as tc
import error_generator as eg
import toric_plot as tp
import unionfind as uf
import uf_plot as up
from tqdm import tqdm
import multiprocessing as mp


def single(size, pE=0, pX=0, pZ=0, savefile=False, erasure_file=None, pauli_file=None, plot_load=False, graph=None, worker=None):
    '''
    Runs the peeling decoder for one iteration
    '''

    # Initialize lattice
    if graph is None:
        graph = go.init_toric_graph(size)

    toric_plot = tp.lattice_plot(graph, plot_size=8, line_width=2) if plot_load else None

    # Initialize errors
    toric_errors = eg.toric(graph, toric_plot=toric_plot, worker=worker)
    toric_errors.init_erasure_region(pE, savefile, erasure_file)
    toric_errors.init_pauli(pX, pZ, savefile, pauli_file)

    # Measure stabiliziers
    tc.measure_stab(graph, toric_plot)

    # Peeling decoder
    uf_plot = up.toric(graph, toric_plot.f, plot_size=8, line_width=1.5, plotstep_click=False) if plot_load else None

    graph.init_bucket(method="C")
    uf.find_clusters(graph, uf_plot=uf_plot, plot_step=0)
    uf.grow_bucket(graph, uf_plot=uf_plot, plot_step=0, step_click=0)
    uf.peel_trees(graph, uf_plot=uf_plot, plot_step=0)

    # Apply matching
    tc.apply_matching_peeling(graph, toric_plot)

    # Measure logical operator
    logical_error = tc.logical_error(graph)
    graph.reset()
    correct = True if logical_error == [False, False, False, False] else False
    return correct


def multiple(size, iters, pE=0, pX=0, pZ=0, plot_load=False, qres=None, worker=None):
    '''
    Runs the peeling decoder for a number of iterations. The graph is reused for speedup.
    '''
    graph = go.init_toric_graph(size)
    result = [single(size, pE, pX, pZ, plot_load=plot_load, graph=graph, worker=worker) for i in tqdm(range(iters))]
    N_succes = sum(result)
    if qres is not None:
        qres.put(N_succes)
    else:
        return N_succes


def multiprocess(size, iters, pE=0, pX=0, pZ=0, processes=None):
    '''
    Runs the peeling decoder for a number of iterations, split over a number of processes
    '''

    if processes is None:
        processes = mp.cpu_count()

    # Calculate iterations for ieach child process
    process_iters = iters//processes
    rest_iters = iters - process_iters*processes

    # Initiate processes
    qres = mp.Queue()
    workers = []
    for i in range(processes-1):
        workers.append(mp.Process(target=multiple, args=(size, process_iters, pE, pX, pZ, False, qres, i)))
    workers.append(mp.Process(target=multiple, args=(size, process_iters + rest_iters, pE, pX, pZ, False, qres, processes - 1)))

    # Start and join processes
    for worker in workers:
        worker.start()
    print("Started", processes, "workers.")
    for worker in workers:
        worker.join()

    results = [qres.get() for worker in workers]
    return sum(results)
