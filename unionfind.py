import random

# Helper functions

def find_cluster_root(cluster):
    '''
    :param cluster      input cluster

    Loops through the cluster tree to find the root cluster of the given cluster. When the parent cluster is not at the root level, the function is started again on the parent cluster. The recursiveness of the function makes sure that at each level the parent is pointed towards the root cluster, furfilling the collapsing rule.
    '''
    if cluster is not None:
        if cluster is not cluster.parent and cluster.parent is not cluster.parent.parent:
            cluster.parent = find_cluster_root(cluster.parent)
        return cluster.parent
    else:
        return None


def union_clusters(parent, child):
    '''
    :param parent       parent cluster
    :param child        child cluster

    Merges two clusters by updating the parent/child relationship and updating the attributes
    '''
    child.parent = parent
    parent.size += child.size
    parent.parity += child.parity
    parent.new_bound.extend(child.new_bound)


def cluster_new_vertex(graph, cluster, vertex, random_traverse=True, uf_plot=None, plot_step=False):
    '''
    :param cluster          current cluster
    :param vertex           vertex that is recently added to the cluster

    Recursive function which adds all connected erasure edges to a cluster, or finds the boundary on a vertex.

    For a given vertex, this function finds the neighboring edges and vertices that are in the the currunt cluster. Any new vertex or edge will be added to the graph.
    If the newly found edge is part of the erasure, the edge and the corresponding vertex will be added to the cluster, and the function is started again on the new vertex. Otherwise it will be added to the boundary.
    If a vertex is an anyon, its property and the parity of the cluster will be updated accordingly.
    '''

    traverse_wind = random.sample(graph.wind, 4) if random_traverse else graph.wind

    for wind in traverse_wind:
        if wind in vertex.neighbors:
            (new_vertex, new_edge) = vertex.neighbors[wind]

            if new_edge.erasure:
                if new_edge.support == 0 and not new_edge.peeled:    # if edge not already traversed
                    if new_vertex.cluster is None:                      # if no cycle detected
                        new_edge.support = 2
                        cluster.add_vertex(new_vertex)
                        if uf_plot is not None and plot_step:
                            uf_plot.plot_edge_step(new_edge, "confirm")
                        cluster_new_vertex(graph, cluster, new_vertex, random_traverse, uf_plot, plot_step)
                    else:                                               # cycle detected, peel edge
                        new_edge.peeled = True
                        if uf_plot is not None and plot_step:
                            uf_plot.plot_edge_step(new_edge, "remove")
            else:
                if new_vertex.cluster is not cluster:                   # Make sure new bound does not lead to self
                    cluster.new_bound.append((vertex, new_edge, new_vertex))


def cluster_place_bucket(graph, cluster, extra=0):
    '''
    :param cluster      current cluster

    The inputted cluster has undergone a size change, either due to cluster growth or during a cluster merge, in which case the new root cluster is inputted. We increase the appropiate bucket number of the cluster intil the fitting bucket has been reached. The cluster is then appended to that bucket.
    If the max bucket number has been reached. The cluster is appended to the wastebasket, which will never be selected for growth.
    '''
    cluster.bucket = cluster.size - 1 + cluster.support

    if cluster.parity % 2 == 1 and cluster.bucket < graph.numbuckets:
        graph.buckets[cluster.bucket].append(cluster)
        if cluster.bucket > graph.maxbucket:
            graph.maxbucket = cluster.bucket
    else:
        cluster.bucket = None


# Main functions


def find_clusters(graph, uf_plot=None, plot_step=False):
    '''
    Given a set of erased qubits/edges on a lattice, this functions finds all edges that are connected and sorts them in separate clusters. A single anyon can also be its own cluster.
    It loops over all vertices (randomly if toggled, which produces a different tree), and calls {cluster_new_vertex} to find all connected erasure qubits, and finds the boundary for growth step 1. Afterwards the cluster is placed in a bucket based in its size.

    '''

    # init bucket
    graph.numbuckets = graph.size*(graph.size//2-1)*2
    graph.buckets = [[] for _ in range(graph.numbuckets)]
    graph.wastebasket = []
    graph.maxbucket = 0


    cID = 0
    vertices = graph.V.values()
    vertices = random.sample(set(vertices), len(vertices)) # Random order: Doesn't matter when pE == 0

    anyons = [vertex for vertex in vertices if vertex.state]

    for vertex in anyons:
        if vertex.cluster is None:
            cluster = graph.add_cluster(cID)
            cluster.add_vertex(vertex)
            cluster_new_vertex(graph, cluster, vertex, uf_plot=uf_plot, plot_step=plot_step)
            cluster_place_bucket(graph, cluster)
            cID += 1

    if uf_plot is not None and not plot_step:
        uf_plot.plot_removed(graph, "Clusters initiated.")
    elif uf_plot is not None:
        uf_plot.waitforkeypress("Clusters initiated.")


def grow_clusters(graph, uf_plot=None, plot_step=False):

    '''
    Grows the clusters, and merges them until there are no uneven clusters left.
    Starting from the lowest bucket, clusters are popped from the list and grown with {grow_cluster}. Due to the nature of how clusters are appended to the buckets, a cluster needs to be checked for 1) root level 2) bucket level and 3) parity before it can be grown.

    '''

    plot = True if uf_plot is not None else False

    for bucket_i, bucket in enumerate(graph.buckets):

        if bucket_i > graph.maxbucket:                  # Break from upper buckets if top bucket has been reached.
            if uf_plot is not None:
                txt = "Max bucket number reached."
                uf_plot.waitforkeypress(txt) if plot else input(txt + " Press any key to continue...\n")
            break

        if bucket == []:                                # no need to check empty bucket
            continue

        txt = "Growing bucket #" + str(bucket_i) + "/" + str(graph.maxbucket) + "."
        if plot and plot_step:
            print(txt)

        Fusion = []        # Initiate Fusion list

        for cluster in bucket:                          # Loop over all clusters in the current bucket
            cluster = find_cluster_root(cluster)
            if cluster.bucket == bucket_i and cluster.new_bound != []:  # Check that cluster is not already in a higher bucket and whether this bucket has new boundaries. If not, this cluster is already grown

                cluster.boundary = cluster.new_bound    # Set boudary
                cluster.new_bound = []
                cluster.support = 1 - cluster.support   # Grow cluster support for bucket placement
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

        while bucket != []:             # Put clusters in new buckets. Some will be added double, but will be skipped by the new_boundary check
            cluster = bucket.pop()
            cluster = find_cluster_root(cluster)
            cluster_place_bucket(graph, cluster)

        if plot and not plot_step:
            uf_plot.draw_plot(txt)


def peel_clusters(graph, uf_plot=None, plot_step=False):
    '''
    Loops overal all vertices to find pendant vertices which are selected from peeling using {peel_edge}

    '''

    def peel_edge(graph, cluster, vertex, uf_plot, plot_step):
        '''
        :param cluster          current active cluster
        :param vertex           pendant vertex of the edge to be peeled

        Recursive function which peels a branch of the tree if the input vertex is a pendant vertex

        If there is only one neighbor of the input vertex that is in the same cluster, this vertex is a pendant vertex and can be peeled. The function calls itself on the other vertex of the edge leaf.
        '''
        plot = True if uf_plot is not None and plot_step else False
        num_connect = 0
        for wind in graph.wind:
            (NV, NE) = vertex.neighbors[wind]
            if NE.support == 2:
                new_cluster = find_cluster_root(NV.cluster)
                if new_cluster is cluster and not NE.peeled:
                    num_connect += 1
                    edge, new_vertex = NE, NV
            if num_connect > 1:
                break
        if num_connect == 1:
            edge.peeled = True
            if vertex.state:
                edge.matching = True
                vertex.state = False
                new_vertex.state = not new_vertex.state
                if plot:
                    uf_plot.plot_edge_step(edge, "match")
                    uf_plot.plot_strip_step_anyon(vertex)
                    uf_plot.plot_strip_step_anyon(new_vertex)
            else:
                uf_plot.plot_edge_step(edge, "peel") if plot else None
            peel_edge(graph, cluster, new_vertex, uf_plot, plot_step)

    for vertex in graph.V.values():
        if vertex.cluster is not None:
            cluster = find_cluster_root(vertex.cluster)
            peel_edge(graph, cluster, vertex, uf_plot, plot_step)

    uf_plot.plot_removed(graph, "Peeling completed.") if uf_plot is not None and not plot_step else None
