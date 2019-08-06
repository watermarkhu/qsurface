import toric_lat as tl
from tqdm import tqdm
import multiprocessing as mp


def single(size, pE=0, pX=0, pZ=0, savefile=False, erasure_file=None, pauli_file=None, plot_load=False, graph=None, worker=None, plot_size=6):
    '''
    Runs the peeling decoder for one iteration
    '''

    if graph is None:
        TL = tl.lattice(size, pauli_file, erasure_file, plot_load, worker=worker, plot_size=plot_size)
    else:
        TL = tl.lattice(size, pauli_file, erasure_file, plot_load, graph=graph, worker=worker, plot_size=plot_size)
    TL.init_erasure_errors_region(pE, savefile)
    TL.init_pauli_errors(pX, pZ, savefile)
    TL.measure_stab()
    TL.get_matching_peeling()
    logical_error = TL.logical_error()
    TL.G.reset()
    correct = True if logical_error == [False, False, False, False] else False
    return correct


def multiple(size, iters, pE=0, pX=0, pZ=0, plot_load=False, qres=None, worker=None, plot_size=6):
    '''
    Runs the peeling decoder for a number of iterations. The graph is reused for speedup.
    '''

    TL = tl.lattice(size)
    result = [single(size, pE, pX, pZ, plot_load=plot_load, graph=TL.G, worker=worker, plot_size=plot_size) for i in tqdm(range(iters))]
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
