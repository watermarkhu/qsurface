import graph_objects as go
import toric_code as tc
import toric_error as te
import unionfind as uf
import pickling as pk
from progiter import ProgIter
import multiprocessing as mp
import cposguf_cluster_actions as cca
from collections import defaultdict as dd
from cluster_per_size import coordinates

def d0(): return [0,0]
def d1(): return [[0,0], [0,0]]
def d2(): return dd(d1)

minl, maxl = 1, 4
clist = coordinates(minl, maxl)
data = pk.load_obj("sim4_r1c_data_gauss12_44-1-4")
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


def single(size, pX=0, graph=None, worker=0, iter=0):

    """
    Runs the peeling decoder for one iteration
    """

    size, pX, graph, worker, iter = 32, 0.089, None, 0, 0

    # Initialize lattice
    if graph is None:
        graph = go.init_toric_graph(size)
    else:
        graph.reset()

    # Initialize errors
    te.init_random_seed(worker=worker, iteration=iter)
    te.init_pauli(graph, pX)

    # errors = [
    #     graph.E[(0, y, x, td)].qID[1:]
    #     for y in range(size) for x in range(size) for td in range(2)
    #     if graph.E[(0, y, x, td)].state
    # ]
    # n = len(errors)
    # choice = "tree" if n < size**2*0.2 else "list"

    # Measure stabiliziers
    tc.measure_stab(graph)

    ufg = uf.cluster_farmer(graph)
    # ufg.find_clusters()

    errors = [
        graph.E[(0, y, x, td)].qID[1:]
        for y in range(size) for x in range(size) for td in range(2)
        if graph.E[(0, y, x, td)].state
    ]

    # Get clusters from array data
    clusters = cca.get_clusters_from_list(errors, size)


    # ufg.tree_grow_bucket(graph.buckets[0], 0)
    #
    # clusters = dd(list)
    # for y in range(size):
    #     for x in range(size):
    #         for td in range(2):
    #             cluster = uf.find_cluster_root(graph.E[(0, y, x, td)].cluster)
    #             if cluster is not None:
    #                 clusters[cluster.cID].append((y, x, td))

    clusters = [
        cluster
        for cluster in clusters.values()
        if len(cluster) >= minl and len(cluster) <= maxl
    ]

    count = get_count(clusters, clist, size)
    count
    norm = [cc[0][0] - cc[1][0] for cc in [data_p[cl][(size, pX)] for cl in clist]]

    # Old norm
    # norm = [(ra**2-1)/(oc**.1) for oc, ra in zip(norm_avg_occ_p[(size, pX)], tl_ratio_p[(size, pX)])]

    cval = [co*no for co, no in zip(count, norm)]

    choice = "tree" if sum(cval[0:]) >= 0 else "list"

    # graph.grow_reset()
    ufg.find_clusters()
    ufg.grow_clusters(method=choice)
    ufg.peel_clusters()

    # Apply matching
    tc.apply_matching_peeling(graph)

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

    graph = go.init_toric_graph(size)
    result = [
        single(size, pX, graph, worker, i)
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


res = multiprocess(8, 30000, 0.089)
print_threshold(res)

# L = [8 + 4*i for i in range(7)]
# P = [(90 + 2*i)/1000 for i in range(11)]
# N = 10000
# database = {}
# for l in L:
#     for p in P:
#         res = multiprocess(l, N, p)
#         print_threshold(res)
#         database[(l, p)] = res
#         pk.save_obj(database, "r1tl_threshold_p_norm0")
