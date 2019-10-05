import random
from unionfind import cluster_new_vertex, find_cluster_root, union_clusters, peel_clusters


# Main functions

def find_clusters(graph, uf_plot=None, plot_step=0, random_order=1):
    '''
    Given a set of erased qubits/edges on a lattice, this functions finds all edges that are connected and sorts them in separate clusters. A single anyon can also be its own cluster.
    It loops over all vertices (randomly if toggled, which produces a different tree), and calls {cluster_new_vertex} to find all connected erasure qubits, and finds the boundary for growth step 1. Afterwards the cluster is placed in a bucket based in its size.

    '''

    # init grow list List
    graph.L = []

    cID = 0
    vertices = graph.V.values()

    # Random order: Doesn't matter when pE == 0
    if random_order:
        vertices = random.sample(set(vertices), len(vertices))

    anyons = [vertex for vertex in vertices if vertex.state]

    for vertex in anyons:
        if vertex.cluster is None:
            cluster = graph.add_cluster(cID)
            cluster.add_vertex(vertex)
            cluster_new_vertex(graph, cluster, vertex, uf_plot=uf_plot, plot_step=plot_step)
            if cluster.parity % 2 == 1:
                graph.L.append(cluster)
            cID += 1

    if uf_plot is not None and not plot_step:
        uf_plot.plot_removed(graph, "Clusters initiated.")
    elif uf_plot is not None:
        uf_plot.waitforkeypress("Clusters initiated.")


def grow_clusters(graph, uf_plot=None, plot_step=0):

    '''
    Grows the clusters, and merges them until there are no uneven clusters left.
    Starting from the lowest bucket, clusters are popped from the list and grown with {grow_cluster}. Due to the nature of how clusters are appended to the buckets, a cluster needs to be checked for 1) root level 2) bucket level and 3) parity before it can be grown.

    '''

    plot = True if uf_plot is not None else False

    while graph.L != []:

        Fusion = []        # Initiate Fusion list

        for cluster in graph.L:                          # Loop over all clusters in the current bucket
            cluster = find_cluster_root(cluster)
            if cluster.new_bound != []:  # Check that cluster is not already in a higher bucket and whether this bucket has new boundaries. If not, this cluster is already grown

                cluster.boundary = cluster.new_bound    # Set boudary
                cluster.new_bound = []
                for vertex, new_edge, new_vertex in cluster.boundary:   # Grow boundaries by half-edge
                    if new_edge.support != 2:
                        new_edge.support += 1
                        if new_edge.support == 2:       # Apped to fusion list of edge fully grown
                            Fusion.append((vertex, new_edge, new_vertex))
                        else:                           # Half grown edges are added immediately to new boundary
                            cluster.new_bound.append((vertex, new_edge, new_vertex))
                        uf_plot.add_edge(new_edge, vertex) if plot else None
                uf_plot.draw_plot(str(cluster) + " grown.") if plot and plot_step else None

        for base_vertex, edge, grow_vertex in Fusion:
            base_cluster = find_cluster_root(base_vertex.cluster)
            grow_cluster = find_cluster_root(grow_vertex.cluster)
            if grow_cluster is None:                    # Fully grown edge. New vertex is on the old boundary. Find new boundary on vertex
                base_cluster.add_vertex(grow_vertex)
                cluster_new_vertex(graph, base_cluster, grow_vertex)
            elif grow_cluster is base_cluster:          # Edge grown on itself. This cluster is already connected. Cut half-edge
                edge.support -= 1
                uf_plot.add_edge(edge, base_vertex) if plot else None
            else:                                       # Clusters merge by weighted union
                if grow_cluster.size < base_cluster.size:
                    base_cluster, grow_cluster = grow_cluster, base_cluster
                union_clusters(grow_cluster, base_cluster)

        uf_plot.draw_plot("Clusters merged") if plot and plot_step else None

        temp_L = []
        while graph.L != []:             # Put clusters in new buckets. Some will be added double, but will be skipped by the new_boundary check
            cluster = graph.L.pop()
            cluster = find_cluster_root(cluster)
            if cluster.parity % 2 == 1:
                temp_L.append(cluster)
        graph.L = temp_L

        if plot and not plot_step:
            uf_plot.draw_plot("Growing...")
