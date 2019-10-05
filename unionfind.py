import random


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


def cluster_place_bucket(graph, cluster, vcomb=0):
    '''
    :param cluster      current cluster

    The inputted cluster has undergone a size change, either due to cluster growth or during a cluster merge, in which case the new root cluster is inputted. We increase the appropiate bucket number of the cluster intil the fitting bucket has been reached. The cluster is then appended to that bucket.
    If the max bucket number has been reached. The cluster is appended to the wastebasket, which will never be selected for growth.
    '''

    cluster.bucket = cluster.size - 1 + cluster.support if vcomb else 2*(cluster.size - 1) + cluster.support

    if cluster.parity % 2 == 1 and cluster.bucket < graph.numbuckets:
        graph.buckets[cluster.bucket].append(cluster)
        if cluster.bucket > graph.maxbucket:
            graph.maxbucket = cluster.bucket
    else:
        cluster.bucket = None


def cluster_new_vertex(graph, cluster, vertex, random_traverse=0, uf_plot=None, plot_step=0):
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
                    cluster.boundary[0].append((vertex, new_edge, new_vertex))


def peel_clusters(graph, uf_plot=None, plot_step=0):
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
