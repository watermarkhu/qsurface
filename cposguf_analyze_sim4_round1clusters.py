import cposguf_cluster_actions as cca
from cposguf_run import sql_connection, fetch_query
import matplotlib.pyplot as plt
from progiter import ProgIter
import graph_objects as go
import toric_error as te
from collections import defaultdict as dd
import pickle
import os


limit = None
minl, maxl = 1, 3
plotnum = 25
maxfetch = 10000
L = [16 + 4 * i for i in range(8)]
file = "sim4_r1c_data"
con, cur = sql_connection()

def save_obj(obj, name):
    with open(name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj(name):
    with open(name + '.pkl', 'rb') as f:
        return pickle.load(f)

def d1(): return [0,0]
def d2(): return dd(d1)

if os.path.exists(file + ".pkl"):
    print("loading data " + file)
    data = load_obj(file)
    data_p, data_n = data["data_p"], data["data_n"]
    countp, countn = data["countp"], data["countn"]
else:
    data_p, data_n = [dd(d2) for _ in range(2)]
    countp, countn = [dd(d1) for _ in range(2)]
    cur.execute("SELECT lattice, p, tree_wins, list_wins FROM cases")
    cases = cur.fetchall()
    for l, p, tn, ln in cases:
        countp[(l, float(p))] = [tn, ln]

for l in L:
    p = None

    print("Getting count...")
    con, cur = sql_connection()
    cur.execute(fetch_query("COUNT(*)", l, p))
    num = cur.fetchone()[0]

    print("Executing query... (be patient)")
    cur.execute(fetch_query("sim_id, lattice, p, ftree_tlist, seed", l, p))

    sims = [cur.fetchone()]

    graph = go.init_toric_graph(l)

    fetched = 1
    new_data = []
    while sims != [None]:
        print("{:0.1f}%".format(fetched/num*100))
        sims += cur.fetchmany(maxfetch)
        fetched += maxfetch

        for sim_id, lattice, p, type, seed in sims:

            te.apply_random_seed(seed)
            te.init_pauli(graph, pX=float(p))

            errors = [
                graph.E[(0, y, x, td)].qID[1:]
                for y in range(lattice) for x in range(lattice) for td in range(2)
                if graph.E[(0, y, x, td)].state
            ]
            n = len(errors)
            new_data.append((n, sim_id))

            # Get clusters from array data
            clusters = cca.get_clusters_from_list(errors, lattice)

            # Remove single clusters
            clusters = [
                cluster
                for cluster in clusters.values()
                if len(cluster) >= minl and len(cluster) <= maxl
            ]

            data_p = cca.get_count2(clusters, data_p, lattice, float(p), type)
            data_n = cca.get_count2(clusters, data_n, lattice, n, type)
            countn[(lattice, n)][type] += 1

            graph.reset()

        sims = [cur.fetchone()]

    # print("Don't kill process now. Updating database...")
    # query = "UPDATE simulations SET n = %s, analysis1 = TRUE WHERE sim_id = %s"
    #
    # con, cur = sql_connection()
    # for this_data in ProgIter(new_data):
    #     cur.execute(query, this_data)
    # cur.close()
    # con.close()

    data = {
        "data_p": data_p,
        "data_n": data_n,
        "countp": countp,
        "countn": countn
    }
    save_obj(data, file)
    print("Process can now be killed")

cur.close()
con.close()


# sorted(cluster_data.items(), key=lambda kv: sum(kv[1]), reverse=True)

# fig = cca.plot_clusters(clusters, count, plotnum)
#
# folder = "../../../OneDrive - Delft University of Technology/MEP - thesis Mark/Simulations/cposguf_sim3_round1clusters/"
# file_name = "cposguf_sim3_L-"
# file_name += "None_p-" if l is None else "{0:d}_p-".format(l)
# file_name += "None" if p is None else "{0:.3f}".format(p)
# fname = folder + "figures/" + file_name + ".pdf"
# fig.savefig(fname, transparent=True, format="pdf", bbox_inches="tight")
# plt.close(fig)
#
# f = open(folder + "data/" + file_name + ".txt", "w")
# f.write("Count: " + str(count))
# for line in clusters:
#     f.write(str(line) + "\n")
# f.close()
