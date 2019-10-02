from cposguf_run import sql_connection, fetch_query
from collections import defaultdict
from matplotlib import pyplot as plt
from matplotlib.lines import Line2D
from cposguf_run import input_error_array
from cposguf_plotcompare import plot_both
import cposguf_cluster_actions as cca
import graph_objects as go
import toric_code as tc
import unionfind_tree as uf


def get_clusters_from_graph(graph, matching=False):
    '''
    returns a tuple of tuples of all the clusters currently in the graph, based on the parent of the qubits
    '''
    clusters = defaultdict(list)
    for qubit in [graph.E[(0, y, x, td)] for y in range(graph.size) for x in range(graph.size) for td in range(2)]:
        if qubit.cluster is not None:
            if matching and not qubit.matching:
                continue
            cluster = uf.find_cluster_root(qubit.cluster)
            clusters[cluster.cID].append(qubit.qID[1:])
    return cca.tupleit(list(clusters.values()))


def get_states_from_graph(graph):
    '''
    Returns the qubits in the graph that have value 1
    '''
    return [(y, x, td) for y in range(graph.size) for x in range(graph.size) for td in range(2) if graph.E[(0, y, x, td)].state]


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


def analyze_sim1(query, minl, maxl, maxfetch=10000):
    con, cur = sql_connection()

    print("Executing query... (be patient)")
    print("SQL:", query)

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
    clusters, count = analyze_sim1(query, minl, maxl)
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
    f.close()


def analyze_sim2_A(sims):

    lattice, p, type, array = sims[3]

    graph = go.init_toric_graph(lattice)
    graph_v = go.init_toric_graph(lattice)
    plot_both(graph, graph_v, array)

    input_error_array(graph, array)
    tc.measure_stab(graph)
    initial_state = get_states_from_graph(graph)
    uf.find_clusters(graph)
    uf.grow_clusters(graph)
    uf.peel_clusters(graph)
    ups = get_clusters_from_graph(graph, matching=1)
    tc.apply_matching_peeling(graph)
    ufs = get_states_from_graph(graph)


    graph.reset()

    input_error_array(graph, array)
    tc.measure_stab(graph)
    uf.find_clusters(graph, vcomb=1)
    uf.grow_clusters(graph, vcomb=1)
    uf.peel_clusters(graph)
    vps = get_clusters_from_graph(graph, matching=1)
    tc.apply_matching_peeling(graph)
    vfs = get_states_from_graph(graph)

    graph.reset()

    efs, cfs = (ufs, vfs) if type else (vfs, ufs)

    e_dict_clusters = cca.get_clusters_from_list(efs, lattice)
    logical_vertices = cca.get_logical_cluster(e_dict_clusters, lattice)

    peel_union = set(cca.flatten(ups)) | set(cca.flatten(vps))
    peel_dict = cca.get_clusters_from_list(list(peel_union), lattice)

    involved_vertices = set(ufs) | set(vfs)

    for cluster in peel_dict.values():
        for qubit in cluster:
            if qubit in involved_vertices:
                involved_vertices = involved_vertices | set(cluster)
                break

    involved_errors = set(initial_state) & (set(involved_vertices))

    plt.figure(3)

    ax = plt.subplot(3,3,1)
    ax.set_title("UBUCK end state (UES)")
    cca.plot_cluster(vfs, lattice-1, lattice-1, ax=ax)

    ax = plt.subplot(3,3,2)
    ax.set_title("VCOMB end state (VES)")
    cca.plot_cluster(ufs, lattice-1, lattice-1, ax=ax)

    ax = plt.subplot(3,3,3)
    ax.set_title("Errors")
    cca.plot_cluster(initial_state, lattice-1, lattice-1, ax=ax)

    ax = plt.subplot(3,3,4)
    ax.set_title("UBUCK matching (UM)")
    cca.plot_cluster(cca.flatten(ups), lattice-1, lattice-1, ax=ax)

    ax = plt.subplot(3,3,5)
    ax.set_title("VCOMB matching (VM)")
    cca.plot_cluster(cca.flatten(vps), lattice-1, lattice-1, ax=ax)

    ax = plt.subplot(3,3,6)
    ax.set_title("UM $\cup$ VM")
    cca.plot_cluster(peel_union , lattice-1, lattice-1, ax=ax)

    ax = plt.subplot(3,3,7)
    ax.set_title("Logical qubits")
    cca.plot_cluster(logical_vertices, lattice-1, lattice-1, ax=ax)

    ax = plt.subplot(3,3,8)
    ax.set_title("Involved qubits")
    cca.plot_cluster(involved_vertices, lattice-1, lattice-1, ax=ax)

    ax = plt.subplot(3,3,9)
    ax.set_title("Involved errors")
    cca.plot_cluster(involved_errors, lattice-1, lattice-1, ax=ax)

    plt.draw()
    plt.show()

    graph_v = go.init_toric_graph(lattice)
    plot_both(graph, graph_v, list(map(list, zip(*involved_errors))))


# p = 0.1
# l = 12
#
# con, cur = sql_connection()
# extra = "analysis_A = FALSE "
# query = fetch_query("lattice, p, vcomb_solved, error_data", p, l, extra=extra)
# cur.execute(query)
# sims = cur.fetchall()
#
# cur.close()
# con.close()
#
# analyze_sim2_A(sims)
