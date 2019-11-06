import sys

sys.path.append("../")
import cposguf_cluster_actions as cca
from cposguf_run import sql_connection, fetch_query
import matplotlib.pyplot as plt
from collections import defaultdict

def count_round0clusters(query, minl, maxl, maxfetch=10000):
    con, cur = sql_connection()

    print("Executing query... (be patient)")

    cur.execute(query)

    cluster_data, type_count = defaultdict(lambda:[0, 0]), [0, 0]
    sims = [cur.fetchone()]

    while sims != [None]:
        print("Fetching data... (" + str(maxfetch) + " rows)")
        sims += cur.fetchmany(maxfetch)

        print("Counting clusters...")
        for lattice, p, type, array in sims:

            # Get clusters from array data
            clusters = cca.get_clusters_from_list(
                zip(array[0], array[1], array[2]), lattice
            )

            # Remove single clusters
            clusters = [
                cluster
                for cluster in clusters.values()
                if len(cluster) >= minl and len(cluster) <= maxl
            ]

            cluster_data = cca.get_count(clusters, cluster_data, lattice, type)

            type_count[type] += 1

        sims = [cur.fetchone()]
    else:
        cur.close()
        con.close()

    return (
        sorted(cluster_data.items(), key=lambda kv: sum(kv[1]), reverse=True),
        type_count,
    )


if __name__ == "__main__":

    L = [20 + 4 * i for i in range(6)]
    P = [i / 1000 for i in [103 + i for i in range(8)]]

    combi = list(zip([None] * len(P), P))
    limit = None
    minl, maxl = 2, 7
    plotnum = 25

    for l, p in combi:
        print("Now doing L = {}, p {}".format(l, p))

        query = fetch_query("lattice, p, vcomb_solved, error_data", p, l, limit=limit)
        clusters, count = count_round0clusters(query, minl, maxl)
        fig = cca.plot_clusters(clusters, count, plotnum)

        folder = "../../../OneDrive - Delft University of Technology/MEP - thesis Mark/Simulations/cposguf_sim1/"
        file_name = "cposguf_sim1_L-"
        file_name += "None_p-" if l is None else "{0:d}_p-".format(l)
        file_name += "None" if p is None else "{0:.3f}".format(p)
        fname = folder + "figures/" + file_name + ".pdf"
        fig.savefig(fname, transparent=True, format="pdf", bbox_inches="tight")
        plt.close(fig)

        f = open(folder + "data/" + file_name + ".txt", "w")
        f.write("Count: " + str(count))
        for line in clusters:
            f.write(str(line) + "\n")
    #     f.close()
