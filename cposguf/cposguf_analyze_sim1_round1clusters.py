import sys
sys.path.append("../")
import cposguf_cluster_actions as cca
from cposguf_run import sql_connection, fetch_query
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D


def get_count(clusters, cluster_data, size, type):
    '''
    returns a defaultdict of lists of clusters countaining the tuples of the qubits
    '''
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
            if cluster in cluster_data:
                cluster_data[cluster][type] += 1
                break
            mcluster = cca.mirror(cluster, dim[0])
            mdim = cca.max_dim(mcluster)
            augs.append(mcluster)
            cmid.append(mdim[1])
            if mcluster in cluster_data:
                cluster_data[mcluster][type] += 1
                break
            cluster = cca.rotate(cluster, dim[0])
        else:
            tupcluster = augs[cmid.index(min(cmid))]
            cluster_data[tupcluster] = [0, 1] if type else [1, 0]

    return cluster_data


def plot_clusters(data, type_count, plotnum, extra=5):

    print("Plotting...")

    fig = plt.figure(figsize=(16,20))
    plotcols = -int(-plotnum**(1/2)//1)
    plotrows = -(-plotnum//plotcols)
    grid = plt.GridSpec(plotrows + extra, plotcols, wspace=0.4, hspace=0.3)

    maxy, maxx = 0, 0
    for cluster, count in data[:plotnum]:
        for (y, x, td) in cluster:
            maxy = y if y > maxy else maxy
            maxx = x if x > maxx else maxx

    for plot_i, (cluster, _) in enumerate(data[:plotnum]):
        ax = plt.subplot(grid[plot_i//plotcols, plot_i%plotcols])
        ax.set_title(str(plot_i))
        cca.plot_cluster(cluster, maxy, maxx, ax=ax, color='C{}'.format(plot_i%10))

    ax_count1 = plt.subplot(grid[plotrows:,:2])
    ax_count2 = plt.subplot(grid[plotrows:,2:])
    ax_count1.set_ylabel("Normalized occurence")
    ax_count2.set_xlabel("Cluster type")

    CU, CV = [], []
    for i, (_, (cu, cv)) in enumerate(data[:plotnum]):
        CU.append(cu/type_count[0])
        CV.append(cv/type_count[0])

    ax_count1.plot(list(range(plotcols)), CU[:plotcols], ':', alpha=0.1, color='black')
    ax_count1.plot(list(range(plotcols)), CV[:plotcols], '--', alpha=0.1, color='black')
    for i in range(plotcols):
        ax_count1.scatter(i, CU[i], s=50, marker='+', color='C{}'.format(i%10))
        ax_count1.scatter(i, CV[i], s=50, marker='x', color='C{}'.format(i%10))
    ax_count2.plot(list(range(plotcols, plotnum)), CU[plotcols:], ':', alpha=0.1, color='black')
    ax_count2.plot(list(range(plotcols, plotnum)), CV[plotcols:], '--', alpha=0.1, color='black')
    for i in range(plotcols, plotnum):
        ax_count2.scatter(i, CU[i], s=50, marker='+', color='C{}'.format(i%10))
        ax_count2.scatter(i, CV[i], s=50, marker='x', color='C{}'.format(i%10))

    legend_elements = [Line2D([0], [0], ls=":", color='black', marker="+", markersize=10, alpha=0.5, label='ubuck'),
                       Line2D([0], [0], ls="--", color='black', marker="x", markersize=10, alpha=0.5, label='vcomb')]

    # Create the figure
    ax_count2.legend(handles=legend_elements)
    plt.title("Cluster data from {} ubuck wins and {} vcomb wins".format(type_count[0], type_count[1]))
    # plt.show()
    return fig


def count_round0clusters(query, minl, maxl, maxfetch=10000):
    con, cur = sql_connection()

    print("Executing query... (be patient)")

    cur.execute(query)

    cluster_data, type_count = {}, [0, 0]
    sims = [cur.fetchone()]

    while sims != [None]:
        print("Fetching data... (" + str(maxfetch) + " rows)")
        sims += cur.fetchmany(maxfetch)

        print("Counting clusters...")
        for lattice, p, type, array in sims:

            # Get clusters from array data
            clusters = cca.get_clusters_from_list(zip(array[0], array[1], array[2]), lattice)

            # Remove single clusters
            clusters = [cluster for cluster in clusters.values() if len(cluster) >= minl and len(cluster) <= maxl]

            cluster_data = get_count(clusters, cluster_data, lattice, type)

            type_count[type] += 1


        sims = [cur.fetchone()]
    else:
        cur.close()
        con.close()

    return sorted(cluster_data.items(), key=lambda kv: sum(kv[1]), reverse=True), type_count


if __name__ == "__main__":

    L = [20 + 4*i for i in range(6)]
    P = [i/1000 for i in [103 + i for i in range(8)]]

    combi = list(zip([None]*len(P), P))
    combi
    limit = None
    minl, maxl = 2, 7
    plotnum = 25

    for l, p in combi:
        print("Now doing L = {}, p {}".format(l,p))

        query = fetch_query("lattice, p, vcomb_solved, error_data", p, l, limit=limit)
        clusters, count = count_round0clusters(query, minl, maxl)
        fig = plot_clusters(clusters, count, plotnum)

        folder = "../../../OneDrive - Delft University of Technology/MEP - thesis Mark/Simulations/cposguf_sim1/"
        file_name = "cposguf_sim1_L-"
        file_name += 'None_p-' if l is None else "{0:d}_p-".format(l)
        file_name += 'None' if p is None else "{0:.3f}".format(p)
        fname = folder + "figures/" + file_name + ".pdf"
        fig.savefig(fname, transparent=True, format="pdf", bbox_inches="tight")
        plt.close(fig)

        f=open(folder + "data/" + file_name + ".txt", 'w')
        f.write("Count: " + str(count))
        for line in clusters:
            f.write(str(line) + "\n")
    #     f.close()
