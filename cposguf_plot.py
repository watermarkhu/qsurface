import psycopg2 as pgs
from cposguf import read_config, input_error_array
import graph_objects as go
import toric_code as tc
import toric_plot as tp
import unionfind_tree as uf
import uf_plot as up
from matplotlib import pyplot as plt


L = 12
p = 0.09
limit = 10
type = None

comp_id, num_process, iters, sql_config = read_config("./cposguf.ini")
con = pgs.connect(**sql_config)
con.set_session(autocommit=True)
cur = con.cursor()

query = "SELECT * FROM simulations WHERE lattice = {} AND p = {} "
if type == "ubuck":
    query += "AND ubuck_solved = TRUE "
elif type == "vcomb":
    query += "AND vcomb_solved = TRUE "
query += " LIMIT {}"
query = query.format(L, p, limit)
cur.execute(query)
sims = cur.fetchall()
cur.close()
con.close()

def grow(graph, cluster, root_cluster, support, uf_plot, plot_step, vcomb):
    '''
    :param cluster          the current cluster selected for growth
    :param root_cluster     the root cluster of the selected cluster
    :param support       determines the growth state of the initial root cluster

    Recursive function which first grows a cluster's children and then itself.

    There are two distinct growth steps. 1) first half step from a given vertex, the cluster size does not increase, no new edges or vertices are added to the cluster, except for during a merge. 2) second half step in which a new vertex is reached, and the edge is added to the cluster.
    During the inital {find_clusters} function, the initial boundary, which contains edges ready for growth step 1, are added to {full_bound}. {half_bound} which contains the boundary edges for growth step 2, is yet empty. From here, clusters from even buckets go into growth step 1 on edges from {full_bound}, and clusters from uneven buckets go into growth step 2 on edges from "half_bound". New boundary edges are added to the other boundary list.
    After growth, the cluster is placed into a new bucket using {cluster_place_bucket}. If a merge happens, the root cluster of the current cluster is made a child of the pendant root_cluster. And the pendant root cluster is placed in a new bucket instead.
    If a cluster has children, these clusters are grown first. The new boundaries from these child clusters are appended to the root_cluster. Such that a parent does not need to remember its children.
    '''
    root_level = True if cluster == root_cluster else False         # Check for root at beginning
    string = str(cluster) + " grown."
    merge_cluster = None

    while cluster.childs[0] != []:                                 # First go through child clusters
        child_cluster = cluster.childs[0].pop()
        grow(graph, child_cluster, root_cluster, support, uf_plot, plot_step, vcomb)

    # cluster.boundary[0].reverse() if support == 0 else None
    while cluster.boundary[support] != []:
        root_cluster = uf.find_cluster_root(cluster)
        (base_vertex, edge, grow_vertex) = cluster.boundary[support].pop()
        grow_cluster = grow_vertex.cluster
        grrt_cluster = uf.find_cluster_root(grow_cluster)
        if grrt_cluster is None:                    # if new_vertex has no cluster: add to cluster
            edge.support += 1
            if support:
                root_cluster.add_vertex(grow_vertex)
                uf.cluster_new_vertex(graph, root_cluster, grow_vertex)
            else:
                root_cluster.boundary[1].append((base_vertex, edge, grow_vertex))
            uf_plot.add_edge(edge, base_vertex)
        elif grrt_cluster is not root_cluster:      # if new_vertex is from another cluster: union
            edge.support += 1
            if not support and edge.support == 2 or support:
                string += " Merged with " + str(grrt_cluster) + "."
                uf.union_clusters(grrt_cluster, root_cluster)
                merge_cluster = grrt_cluster
                uf_plot.add_edge(edge, base_vertex)
            elif not support:
                root_cluster.boundary[1].append((base_vertex, edge, grow_vertex))
                uf_plot.add_edge(edge, base_vertex)
        else:                                       # if new_vertex is in same cluster: nothing
            None

    cluster.support = 1 - support

    if root_level:          # only at the root level will a cluster be placed in a new bucket
        if merge_cluster is None:
            uf.cluster_place_bucket(graph, root_cluster, vcomb)
        else:
            uf.cluster_place_bucket(graph, merge_cluster, vcomb)

    uf_plot.draw_plot(string) if plot_step else None


def grow_clusters(graph_u, uf_plot_u, graph_v, uf_plot_v, plot_step=0):

    '''
    Grows the clusters, and merges them until there are no uneven clusters left.
    Starting from the lowest bucket, clusters are popped from the list and grown with {grow_cluster}. Due to the nature of how clusters are appended to the buckets, a cluster needs to be checked for 1) root level 2) bucket level and 3) parity before it can be grown.

    '''

    for bucket_i, (bucket_u, bucket_v) in enumerate(zip(graph_u.buckets, graph_v.buckets)):

        if bucket_i > graph_u.maxbucket and bucket_i > graph_v.maxbucket:
            break

        if bucket_u == [] and bucket_v == []:
            continue

        while bucket_u != []:                          # Loop over all clusters in the current bucket\
            cluster = bucket_u.pop()
            root_cluster = uf.find_cluster_root(cluster)
            if root_cluster.bucket == bucket_i:                  # Check that cluster is not already in a higher bucket
                grow(graph_u, root_cluster, root_cluster, root_cluster.support, uf_plot_u, plot_step, vcomb=0)
        while bucket_v != []:                          # Loop over all clusters in the current bucket\
            cluster = bucket_v.pop()
            root_cluster = uf.find_cluster_root(cluster)
            if root_cluster.bucket == bucket_i:                  # Check that cluster is not already in a higher bucket
                grow(graph_v, root_cluster, root_cluster, root_cluster.support, uf_plot_v, plot_step, vcomb=1)

        if not plot_step:
            txt = "Growing bucket #" + str(bucket_i) + "/" + str(max([graph_u.maxbucket, graph_v.maxbucket])) + "."
            uf_plot_u.draw_plot(txt)

    uf_plot_u.waitforkeypress("Clusters grown.")


def plot_final(tp, graph_u, graph_v):
    '''
    param: flips        qubits that have flipped in value (y,x)
    param: arrays       data array of the (corrected) qubit states
    plots the applied stabilizer measurements over the lattices
    also, in the qubits that have flipped in value a smaller white circle is plotted

    optionally, the axis is clear and the final state of the lattice is plotted
    '''

    plt.sca(tp.ax)

    for y in range(tp.size):
        for x in range(tp.size):
            for td in range(2):
                u_error = graph_u.E[(0, y, x, td)].matching
                v_error = graph_v.E[(0, y, x, td)].matching

                qubit = tp.qubits[(y, x, td)]

                if u_error and not v_error:
                    qubit.set_edgecolor([.2, 0, .8])
                    tp.ax.draw_artist(qubit)
                elif v_error and not u_error:
                    qubit.set_edgecolor([.2, .8, 0])
                    tp.ax.draw_artist(qubit)
                elif u_error and v_error:
                    qubit.set_edgecolor([.2, .8, .8])
                    tp.ax.draw_artist(qubit)

    tp.canvas.blit(tp.ax.bbox)
    tp.waitforkeypress("Corrections plotted.")


graph_u = go.init_toric_graph(L)
graph_v = go.init_toric_graph(L)
for _, _, _, comp_id, created_on, ubuck_win, _, array in sims:
    print("Displaying sim by", comp_id, "created on", created_on)
    winner = "UBUCK" if ubuck_win else "VCOMB"
    print("Winner:", winner)


    toric_plot = tp.lattice_plot(graph_u, plot_size=10, line_width=2)

    input_error_array(graph_u, array)
    input_error_array(graph_v, array)
    toric_plot.plot_errors()
    # Measure stabiliziers
    tc.measure_stab(graph_u, toric_plot)
    tc.measure_stab(graph_v)

    # Peeling decoder
    uf_plot_u = up.toric(graph_u, toric_plot.f, axn=2, plot_size=10, line_width=1.5, plotstep_click=0)
    uf_plot_v = up.toric(graph_v, toric_plot.f, axn=3, plot_size=10, line_width=1.5, plotstep_click=0)

    uf.find_clusters(graph_u, uf_plot=uf_plot_u, plot_step=0, vcomb=0)
    uf.find_clusters(graph_v, uf_plot=uf_plot_v, plot_step=0, vcomb=1)

    grow_clusters(graph_u, uf_plot_u, graph_v, uf_plot_v, plot_step=0)

    uf.peel_clusters(graph_u, uf_plot=uf_plot_u, plot_step=0)
    uf.peel_clusters(graph_v, uf_plot=uf_plot_v, plot_step=0)

    # Apply matching
    tc.apply_matching_peeling(graph_u)
    tc.apply_matching_peeling(graph_v)

    plot_final(toric_plot, graph_u, graph_v)

    # Measure logical operator
    graph_u.reset()
    graph_v.reset()
