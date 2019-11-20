import cposguf_cluster_actions as cca
from cposguf_run import sql_connection, fetch_query
import graph_objects as go
import toric_error as te
import toric_code as tc
import unionfind as uf
from collections import defaultdict as dd
import pickling as pk
import os


limit = None
plotnum = 25
maxfetch = 5000
L = [8 + 4 * i for i in range(10)]
P = [(90 + i)/1000 for i in range(21)]
minl, maxl = 1, 6
file = "sim4_realr1c_data_gauss8_44-c1_6"

##############################################
# definitions:

def d0(): return [0,0]
def d1(): return [[0,0], [0,0]]
def d2(): return dd(d1)


def get_count(clusters, data_p, data_n, size, p, n, round, type):
    """
    returns a defaultdict of lists of clusters countaining the tuples of the qubits
    """
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
            if fcluster in data_p:
                data_p[fcluster][(size, p)][round][type] += 1
                data_n[fcluster][(size, n)][round][type] += 1
                break
            mcluster = cca.mirror(cluster, dim[0])
            mdim = cca.max_dim(mcluster)
            augs.append(mcluster)
            cmid.append(mdim[1])
            fmcluster = frozenset(mcluster)
            if fmcluster in data_p:
                data_p[fmcluster][(size, p)][round][type] += 1
                data_n[fmcluster][(size, n)][round][type] += 1
                break
            cluster = cca.rotate(cluster, dim[0])
        else:
            ftupcluster = frozenset(augs[cmid.index(min(cmid))])
            data_p[ftupcluster][(size, p)][round][type] += 1
            data_n[ftupcluster][(size, n)][round][type] += 1

    return data_p, data_n

###########################################################

if os.path.exists(file + ".pkl"):           # Load data_base if pickled file exists
    print("loading data " + file)
    data = pk.load_obj(file)
    data_p, data_n = data["data_p"], data["data_n"]
    countp, countn = data["countp"], data["countn"]
else:                                       # Initate database
    data_p, data_n = [dd(d2) for _ in range(2)]
    countp, countn = [dd(d0) for _ in range(2)]

for lattice in L:
    for p in P:

        con, cur = sql_connection()
        print("\nGetting count of L{}, p{}...".format(lattice, p))
        cur.execute("SELECT tree_wins, list_wins FROM cases WHERE lattice = {} and p = {}".format(lattice, p))
        tlcount = cur.fetchone()
        countp[(lattice, p)] = [tlcount[0], tlcount[1]]

        cur.execute(fetch_query("COUNT(*)", lattice, p))
        num = cur.fetchone()[0]
        print("fetching {} simulations...".format(num))

        cur.execute(fetch_query("ftree_tlist, seed", lattice, p))
        sims = [cur.fetchone()]
        graph = go.init_toric_graph(lattice)

        fetched = 1
        while sims != [None]:

            print("{:0.1f}%".format(fetched/num*100))
            sims += cur.fetchmany(maxfetch-1)
            fetched += maxfetch

            for type, seed in sims:

                # Get errors from seed
                te.apply_random_seed(seed)
                te.init_pauli(graph, pX=float(p))

                n = len([
                    graph.E[(0, y, x, td)].qID[1:]
                    for y in range(lattice) for x in range(lattice) for td in range(2)
                    if graph.E[(0, y, x, td)].state
                ])
                countn[(lattice, n)][type] += 1

                tc.measure_stab(graph)
                ufg = uf.cluster_farmer(graph)
                ufg.find_clusters(plot_step=0)
                grow_bucket = {
                    0: ufg.tree_grow_bucket,
                    1: ufg.list_grow_bucket
                }

                # Analyze clusters after bucket 0 growth
                grow_bucket[type](graph.buckets[0], 0)
                clusters = cca.get_support2clusters(graph, lattice, minl, maxl)
                data_p, data_n = get_count(clusters, data_p, data_n, lattice, p, n, 0, type)

                # Analyze clusters after bucket 1 growth
                grow_bucket[type](graph.buckets[1], 1)
                clusters = cca.get_support2clusters(graph, lattice, minl, maxl)
                data_p, data_n = get_count(clusters, data_p, data_n, lattice, p, n, 1, type)

                graph.reset()
            sims = [cur.fetchone()]
        else:
            print("100%")
            cur.close()
            con.close()

        print("Saving data...")
        data = {    # Save to single data file
            "data_p": data_p,
            "data_n": data_n,
            "countp": countp,
            "countn": countn
        }
        pk.save_obj(data, file)
