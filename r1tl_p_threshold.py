import graph_objects as go
import toric_code as tc
import toric_error as te
import unionfind as uf
import pickling as pk
from progiter import ProgIter
import multiprocessing as mp
import cposguf_cluster_actions as cca
from collections import defaultdict as dd


def clusters1_3(): # All possible clusters between and including size 1 and 3
    return 1, 3, [
        frozenset({(0, 0, 0)}),
        frozenset({(0, 0, 0), (0, 0, 1)}),
        frozenset({(0, 0, 1), (1, 0, 1)}),
        frozenset({(0, 0, 0), (0, 0, 1), (1, 0, 0)}),
        frozenset({(1, 0, 0), (0, 1, 1), (0, 1, 0)}),
        frozenset({(1, 0, 0), (0, 0, 1), (1, 0, 1)}),
        frozenset({(0, 0, 0), (0, 0, 1), (0, 1, 0)}),
        frozenset({(0, 0, 0), (0, 1, 0), (0, 2, 0)})
    ]

minl, maxl, clist = clusters1_3()
tldata = pk.load_obj("sim4_tldata")
tl_ratio_p = tldata["tl_ratio_p"]
norm_avg_occ_p = tldata["norm_avg_occ_p"]

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

    # Initialize lattice
    if graph is None:
        graph = go.init_toric_graph(size)

    # Initialize errors
    te.init_random_seed(worker=worker, iteration=iter)
    te.init_pauli(graph, pX)

    # Measure stabiliziers
    tc.measure_stab(graph)

    ufg = uf.cluster_farmer(graph)
    ufg.find_clusters()
    ufg.tree_grow_bucket(graph.buckets[0], 0)

    clusters = dd(list)
    for y in range(size):
        for x in range(size):
            for td in range(2):
                cluster = uf.find_cluster_root(graph.E[(0, y, x, td)].cluster)
                if cluster is not None:
                    clusters[cluster.cID].append((y, x, td))
    clusters = [
        cluster
        for cluster in clusters.values()
        if len(cluster) >= minl and len(cluster) <= maxl
    ]
    count = get_count(clusters, clist, size)

    cval = [co*oc*(ra-1) for co, oc, ra in zip(count, norm_avg_occ_p[(size, pX)], tl_ratio_p[(size, pX)])]
    choice = 1 - int((sum(cval)+1) // 1)

    if choice == 0:
        ufg.grow_clusters(method="tree", start_bucket=1)
    else:
        graph.grow_reset()
        ufg.find_clusters()
        ufg.grow_clusters(method="list")

    ufg.peel_clusters(plot_step=0)

    # Apply matching
    tc.apply_matching_peeling(graph)

    # Measure logical operator
    logical_error = tc.logical_error(graph)
    graph.reset()
    correct = 1 if logical_error == [False, False, False, False] else 0
    return correct, choice


def multiple(size, iters, pX=0, qres=None, worker=0):
    """
    Runs the peeling decoder for a number of iterations. The graph is reused for speedup.
    """
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
    print("Started", processes, "workers.")
    for worker in workers:
        worker.start()
    for worker in workers:
        worker.join()

    results = [qres.get() for worker in workers]
    suc_count = dd(int)
    for result in results:
        for key, val in result.items():
            suc_count[key] += val

    return suc_count

def d0(): return {(0,0):0, (0,1):0, (1,0):0, (1,1):0}
database = dd(d0)

L = [8 + 4*i for i in range(8)]
P = [(90 + i)/1000 for i in range(11)]
N = 50000

for l in L:
    for p in P:

        print("Calculating for L{}, p{}".format(l,p))
        res = multiprocess(l, N, p)
        print(res)
        for key, val in res.items():
            database[(l, p)][key] += val

        pk.save_obj(database, "r1tl_threshold")
