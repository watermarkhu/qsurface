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
    parent.childs.append(child)
    parent.size += child.size
    parent.parity += child.parity


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
                        new_edge.cluster = cluster
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
                    cluster.add_full_bound(vertex, new_edge, new_vertex)


def cluster_place_bucket(graph, cluster, merge=False):
    '''
    :param cluster      current cluster

    The inputted cluster has undergone a size change, either due to cluster growth or during a cluster merge, in which case the new root cluster is inputted. We increase the appropiate bucket number of the cluster intil the fitting bucket has been reached. The cluster is then appended to that bucket.
    If the max bucket number has been reached. The cluster is appended to the wastebasket, which will never be selected for growth.
    '''
    cluster.bucket = cluster.size - 1
    if not cluster.full_edged:                      # Additional level added if currently in growth state 1
        cluster.bucket += 1

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
    cID = 0
    vertices = graph.V.values()

    # Random order: Doesn't matter when pE == 0
    if False:
        vertices = random.sample(set(vertices), len(vertices))

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


def grow_bucket(graph, uf_plot=None, plot_step=False, step_click=False):

    '''
    Grows the clusters, and merges them until there are no uneven clusters left.
    Starting from the lowest bucket, clusters are popped from the list and grown with {grow_cluster}. Due to the nature of how clusters are appended to the buckets, a cluster needs to be checked for 1) root level 2) bucket level and 3) parity before it can be grown.

    '''
    def grow(graph, cluster, root_cluster, full_edged, uf_plot, plot_step, step_click, family_growth=True):
        '''
        :param cluster          the current cluster selected for growth
        :param root_cluster     the root cluster of the selected cluster
        :param full_edged       determines the growth state of the initial root cluster
        :family_growth          detemines whether growth happens on parent or child cluster

        Recursive function which first grows a cluster's children and then itself.

        There are two distinct growth steps. 1) first half step from a given vertex, the cluster size does not increase, no new edges or vertices are added to the cluster, except for during a merge. 2) second half step in which a new vertex is reached, and the edge is added to the cluster.
        During the inital {find_clusters} function, the initial boundary, which contains edges ready for growth step 1, are added to {full_bound}. {half_bound} which contains the boundary edges for growth step 2, is yet empty. From here, clusters from even buckets go into growth step 1 on edges from {full_bound}, and clusters from uneven buckets go into growth step 2 on edges from "half_bound". New boundary edges are added to the other boundary list.
        After growth, the cluster is placed into a new bucket using {cluster_place_bucket}. If a merge happens, the root cluster of the current cluster is made a child of the pendant root_cluster. And the pendant root cluster is placed in a new bucket instead.
        If a cluster has children, these clusters are grown first. The new boundaries from these child clusters are appended to the root_cluster. Such that a parent does not need to remember its children.
        '''
        plot = True if uf_plot is not None else False
        root_level = True if cluster == root_cluster else False         # Check for root at beginning
        string = str(cluster) + " grown."

        if family_growth:
            while cluster.childs != []:                                 # First go through child clusters
                child_cluster = cluster.childs.pop()
                grow(graph, child_cluster, root_cluster, full_edged, uf_plot, plot_step, step_click)

        merge_cluster = None

        if family_growth:
            cluster.full_edged = not full_edged
        cluster.full_bound.reverse() if full_edged else None
        bound = cluster.full_bound if full_edged else cluster.half_bound
        while bound != []:
            root_cluster = find_cluster_root(root_cluster)
            (base_vertex, edge, grow_vertex) = bound.pop()
            grow_cluster = grow_vertex.cluster
            grrt_cluster = find_cluster_root(grow_cluster)
            if grrt_cluster is None:
                edge.support += 1
                if full_edged:
                    root_cluster.half_bound.append((base_vertex, edge, grow_vertex))
                else:
                    root_cluster.add_vertex(grow_vertex)
                    cluster_new_vertex(graph, root_cluster, grow_vertex)
                uf_plot.add_edge(edge, base_vertex) if plot else None
            else:
                if grrt_cluster is not root_cluster:
                    edge.support += 1
                    if full_edged and edge.support == 2 or not full_edged:
                        string += " Merged with " + str(grrt_cluster) + "."
                        union_clusters(grrt_cluster, root_cluster)
                        merge_cluster = grrt_cluster
                        uf_plot.add_edge(edge, base_vertex) if plot else None
                    elif full_edged:
                        root_cluster.half_bound.append((base_vertex, edge, grow_vertex))
                        uf_plot.add_edge(edge, base_vertex) if plot else None

        if root_level:          # only at the root level will a cluster be placed in a new bucket
            if merge_cluster is None:
                cluster_place_bucket(graph, root_cluster)
            else:
                cluster_place_bucket(graph, merge_cluster, merge=True)

        uf_plot.draw_plot(string) if plot and plot_step else None

    plot = True if uf_plot is not None else False

    for bucket_i, bucket in enumerate(graph.buckets):

        if bucket == []:
            continue

        if bucket_i > graph.maxbucket:                                # Break from upper buckets if top bucket has been reached.
            if uf_plot is not None:
                txt = "Max bucket number reached."
                uf_plot.waitforkeypress(txt) if plot else input(txt + " Press any key to continue...\n")
            break

        while bucket != []:                          # Loop over all clusters in the current bucket
            cluster = bucket.pop()
            root_cluster = find_cluster_root(cluster)
            # if root_cluster is cluster:                                 # Check that cluster is at root
            if root_cluster.bucket == bucket_i:                  # Check that cluster is not already in a higher bucket
                grow(graph, root_cluster, root_cluster, root_cluster.full_edged, uf_plot, plot_step, step_click)
        if plot and not plot_step:
            txt = "Growing bucket #" + str(bucket_i) + "/" + str(graph.maxbucket) + "."
            uf_plot.draw_plot(txt)
    if plot:
        if plot_step:
            input("Clusters grown. Press any key to continue...")
        else:
            uf_plot.waitforkeypress("Clusters grown.")


def peel_trees(graph, uf_plot=None, plot_step=False):
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
