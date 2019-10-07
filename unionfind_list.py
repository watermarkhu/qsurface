import random
from unionfind import cluster_new_vertex, cluster_place_bucket, find_cluster_root, union_clusters, find_clusters, peel_clusters

# Main functions

def grow_clusters(graph, uf_plot=None, plot_step=0, random_traverse=0, vcomb=0, print_steps=0):

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

        if print_steps:
            print("############################ GROW ############################")
            print("Growing bucket", bucket_i, "of", graph.maxbucket, ":", bucket)
            print("Remaining buckets:", graph.buckets[bucket_i+1:graph.maxbucket+1], graph.wastebasket)
            uf_plot.waitforkeypress() if plot else input("Press any key to continue...\n")

        txt = "Growing bucket #" + str(bucket_i) + "/" + str(graph.maxbucket) + "."
        # if plot and plot_step:
        #     print(txt)

        fusion = []        # Initiate Fusion list
        place = []

        for cluster in bucket:                          # Loop over all clusters in the current bucket
            cluster = find_cluster_root(cluster)

            if cluster.bucket == bucket_i:  # Check that cluster is not already in a higher bucket
                place.append(cluster)

                cluster.boundary[1], cluster.boundary[0] = cluster.boundary[0], []  # Set boudary
                cluster.support = 1 - cluster.support   # Grow cluster support for bucket placement
                for vertex, new_edge, new_vertex in cluster.boundary[1]:   # Grow boundaries by half-edge
                    if new_edge.support != 2:
                        new_edge.support += 1
                        if new_edge.support == 2:       # Apped to fusion list of edge fully grown
                            fusion.append((vertex, new_edge, new_vertex))
                        else:                           # Half grown edges are added immediately to new boundary
                            cluster.boundary[0].append((vertex, new_edge, new_vertex))
                        uf_plot.add_edge(new_edge, vertex) if plot else None
                uf_plot.draw_plot(str(cluster) + " grown.") if plot and plot_step else None

        for base_vertex, edge, grow_vertex in fusion:
            base_cluster = find_cluster_root(base_vertex.cluster)
            grow_cluster = find_cluster_root(grow_vertex.cluster)
            if grow_cluster is None:                    # Fully grown edge. New vertex is on the old boundary. Find new boundary on vertex
                base_cluster.add_vertex(grow_vertex)
                cluster_new_vertex(graph, base_cluster, grow_vertex, random_traverse=random_traverse)
            elif grow_cluster is base_cluster:          # Edge grown on itself. This cluster is already connected. Cut half-edge
                edge.support -= 1
                uf_plot.add_edge(edge, base_vertex) if plot else None
            else:                                       # Clusters merge by weighted union
                if grow_cluster.size < base_cluster.size:       # apply weighted union
                    base_cluster, grow_cluster = grow_cluster, base_cluster
                union_clusters(grow_cluster, base_cluster)
                grow_cluster.boundary[0].extend(base_cluster.boundary[0])

        uf_plot.draw_plot("Clusters merged") if plot and plot_step else None

        for cluster in place:             # Put clusters in new buckets. Some will be added double, but will be skipped by the new_boundary check
            cluster = find_cluster_root(cluster)
            cluster_place_bucket(graph, cluster, vcomb)

        if plot and not plot_step:
            uf_plot.draw_plot(txt)
