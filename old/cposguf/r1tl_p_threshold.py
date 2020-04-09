import graph_objects as go
import toric_code as tc
import toric_error as te
import unionfind as uf
import pickling as pk
from progiter import ProgIter
import multiprocessing as mp
import cposguf_cluster_actions as cca
from collections import defaultdict as dd

def d0(): return [0,0]
def d1(): return [[0,0], [0,0]]
def d2(): return dd(d1)

minl, maxl = 1, 4
data = pk.load_obj("sim4_realr1c_data_gauss8_44-c1_6")
data_p = data["data_p"]
countp = data["countp"]



def get_count(clusters, clist, size):
    """
    returns a defaultdict of lists of clusters countaining the tuples of the qubits
    """
    count = [0 for i in clist]
    clusters = cca.listit(clusters)

    # Return to principal cluster
    for i, cluster in enumerate(clusters):
        clusters[i] = cca.principal(cluster, ydim=size, xdim=size)
    for cluster in clusters:
        augs, cmid = [], []
        for rot_i in range(4):
            dim = cca.max_dim(cluster)
            augs.append(cluster)
            cmid.append(dim[1])
            fcluster = frozenset(cluster)
            if fcluster in clist:
                count[clist.index(fcluster)] += 1
                break
            mcluster = cca.mirror(cluster, dim[0])
            mdim = cca.max_dim(mcluster)
            augs.append(mcluster)
            cmid.append(mdim[1])
            fmcluster = frozenset(mcluster)
            if fmcluster in clist:
                count[clist.index(fmcluster)] += 1
                break
            cluster = cca.rotate(cluster, dim[0])
        else:
            ftupcluster = frozenset(augs[cmid.index(min(cmid))])
            count[clist.index(ftupcluster)] += 1

    return count


def single(size, pX=0, graph0=None, graph1=None, worker=0, iter=0):

    """
    Runs the peeling decoder for one iteration
    """

    # size, pX, graph, worker, iter = 28, 0.09, None, 0, 0

    # Initialize lattice

    if graph0 is None:
        graph0 = go.init_toric_graph(size)
    else:
        graph0.reset()
    if graph1 is None:
        graph1 = go.init_toric_graph(size)
    else:
        graph1.reset()

    seed = te.init_random_seed(worker=worker, iteration=iter)
    te.init_pauli(graph0, pX)

    te.apply_random_seed(seed)
    te.init_pauli(graph1, pX)

    tc.measure_stab(graph0)
    tc.measure_stab(graph1)

    uf0 = uf.cluster_farmer(graph0)
    uf1 = uf.cluster_farmer(graph1)

    uf0.find_clusters()
    uf1.find_clusters()

    # Analyze clusters after bucket 0 growth
    uf0.tree_grow_bucket(graph0.buckets[0], 0)
    cl0 = cca.get_support2clusters(graph0, size, minl, maxl)

    uf1.list_grow_bucket(graph1.buckets[0], 0)
    cl1 = cca.get_support2clusters(graph1, size, minl, maxl)

    clist, normc0, normc1 = [], [], []
    for key, val in data_p.items():
        clist.append(key)
        normc0.append(val[(size, pX)][0][0])
        normc1.append(val[(size, pX)][0][1])

    count0 = get_count(cl0, clist, size)
    count1 = get_count(cl1, clist, size)

    num0, num1 = countp[(size, pX)]

    val0 = sum([d/(d+abs(c-d)**1.002) for d, c in [(n/num0, c) for n, c in zip(normc0, count0)] if d > 0 ])
    val1 = sum([d/(d+abs(c-d)**1) for d, c in [(n/num1, c) for n, c in zip(normc1, count1)] if d > 0 ])

    choice = "tree" if val0 > val1 else "list"

    if choice == "tree":
        uf0.grow_clusters(method="tree", start_bucket=1)
        uf0.peel_clusters()
        graph = graph0
    else:
        uf1.grow_clusters(method="list", start_bucket=1)
        uf1.peel_clusters()
        graph = graph1


    # Measure logical operator
    logical_error = tc.logical_error(graph)
    correct = 1 if logical_error == [False, False, False, False] else 0
    return correct, choice


def multiple(size, iters, pX=0, qres=None, worker=None):
    """
    Runs the peeling decoder for a number of iterations. The graph is reused for speedup.
    """
    if worker == None:
        print(f"L = {size}, p = {pX}")
        worker = 0

    graph0 = go.init_toric_graph(size)
    graph1 = go.init_toric_graph(size)
    result = [
        single(size, pX, graph0, graph1, worker, i)
        for i in ProgIter(range(iters))
    ]

    suc_count = dd(int)
    for key in result:
        suc_count[key] += 1

    if qres is not None:
        qres.put(suc_count)
    else:
        return suc_count


def multiprocess(size, iters, pX=0, processes=None):
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
                args=(size, process_iters, pX, qres, i),
            )
        )
    workers.append(
        mp.Process(
            target=multiple,
            args=(size, process_iters + rest_iters, pX, qres, i),
        )
    )

    # Start and join processes
    print(f"\nStarted {processes} workers for L = {size}, p = {pX}")
    for worker in workers:
        worker.start()
    for worker in workers:
        worker.join()

    results = [qres.get() for worker in workers]
    suc_count = {(1, "tree"):0, (1, "list"):0, (0, "tree"):0, (0, "list"):0}
    for result in results:
        for key, val in result.items():
            suc_count[key] += val

    return suc_count

def print_threshold(res):
    tsucc = res[(1, "tree")]
    lsucc = res[(1, "list")]
    tfail = res[(0, "tree")]
    lfail = res[(0, "list")]
    tot = tsucc+tfail+lsucc+lfail
    tthres = 0 if tsucc == 0 else tsucc/(tsucc+tfail)
    lthres = 0 if lsucc == 0 else lsucc/(lsucc+lfail)
    print("tree:", tthres, f"({(tsucc+tfail)/tot*100}%)")
    print("list:", lthres, f"({(lsucc+lfail)/tot*100}%)")
    print("both:", (tsucc+lsucc)/tot)


# res = multiprocess(16, 2000, 0.09)
# print_threshold(res)

L = [8 + 4*i for i in range(7)]
P = [(90 + 2*i)/1000 for i in range(11)]
N = 10000
database = {}
for l in L:
    for p in P:
        res = multiprocess(l, N, p)
        print_threshold(res)
        database[(l, p)] = res
        pk.save_obj(database, "r1tl_threshold_p_norm0")
