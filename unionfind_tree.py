import printing as pr
from unionfind import (
    cluster_new_vertex,
    cluster_place_bucket,
    find_cluster_root,
    union_clusters,
)

# Main functions


def grow(
    graph,
    cluster,
    root_cluster,
    support,
    uf_plot=None,
    plot_step=0,
    random_traverse=0,
    vcomb=0,
):
    """
    :param cluster          the current cluster selected for growth
    :param root_cluster     the root cluster of the selected cluster

    Recursive function which first grows a cluster's children and then itself.

    There are two distinct growth steps. 1) first half step from a given vertex, the cluster size does not increase, no new edges or vertices are added to the cluster, except for during a merge. 2) second half step in which a new vertex is reached, and the edge is added to the cluster.
    During the inital {find_clusters} function, the initial boundary, which contains edges ready for growth step 1, are added to {full_bound}. {half_bound} which contains the boundary edges for growth step 2, is yet empty. From here, clusters from even buckets go into growth step 1 on edges from {full_bound}, and clusters from uneven buckets go into growth step 2 on edges from "half_bound". New boundary edges are added to the other boundary list.
    After growth, the cluster is placed into a new bucket using {cluster_place_bucket}. If a merge happens, the root cluster of the current cluster is made a child of the pendant root_cluster. And the pendant root cluster is placed in a new bucket instead.
    If a cluster has children, these clusters are grown first. The new boundaries from these child clusters are appended to the root_cluster. Such that a parent does not need to remember its children.
    """
    plot = True if uf_plot is not None else False
    root_level = (
        True if cluster == root_cluster else False
    )  # Check for root at beginning
    string = str(cluster) + " grown."
    merge_cluster = None

    while cluster.childs[0] != []:  # First go through child clusters
        child_cluster = cluster.childs[0].pop()
        grow(
            graph,
            child_cluster,
            root_cluster,
            support,
            uf_plot,
            plot_step,
            random_traverse,
            vcomb,
        )

    # cluster.boundary[0].reverse() if support == 0 else None
    while cluster.boundary[support] != []:
        root_cluster = find_cluster_root(cluster)
        (base_vertex, edge, grow_vertex) = cluster.boundary[support].pop()
        grow_cluster = grow_vertex.cluster
        grrt_cluster = find_cluster_root(grow_cluster)
        if grrt_cluster is None:  # if new_vertex has no cluster: add to cluster
            edge.support += 1
            if support:
                root_cluster.add_vertex(grow_vertex)
                edge.cluster = root_cluster
                cluster_new_vertex(
                    graph, root_cluster, grow_vertex, random_traverse=random_traverse
                )
            else:
                root_cluster.boundary[1].append((base_vertex, edge, grow_vertex))
            if plot:
                uf_plot.add_edge(edge, base_vertex)
        elif (
            grrt_cluster is not root_cluster
        ):  # if new_vertex is from another cluster: union
            edge.support += 1
            if not support and edge.support == 2 or support:
                string += " Merged with " + str(grrt_cluster) + "."
                edge.cluster = grrt_cluster
                union_clusters(grrt_cluster, root_cluster)
                grrt_cluster.childs[0].append(root_cluster)
                merge_cluster = grrt_cluster
                if plot:
                    uf_plot.add_edge(edge, base_vertex)
            elif not support:
                root_cluster.boundary[1].append((base_vertex, edge, grow_vertex))
                if plot:
                    uf_plot.add_edge(edge, base_vertex)
        else:  # if new_vertex is in same cluster: nothing
            None

    cluster.support = 1 - support

    if root_level:  # only at the root level will a cluster be placed in a new bucket
        if merge_cluster is None:
            cluster_place_bucket(graph, root_cluster, vcomb)
        else:
            cluster_place_bucket(graph, merge_cluster, vcomb)

    if plot and plot_step:
        uf_plot.draw_plot(string)


def grow_clusters(graph, uf_plot=None, plot_step=0, random_traverse=0, vcomb=0):

    """
    Grows the clusters, and merges them until there are no uneven clusters left.
    Starting from the lowest bucket, clusters are popped from the list and grown with {grow_cluster}. Due to the nature of how clusters are appended to the buckets, a cluster needs to be checked for 1) root level 2) bucket level and 3) parity before it can be grown.

    """

    plot = True if uf_plot is not None else False

    for bucket_i, bucket in enumerate(graph.buckets):

        if (
            bucket_i > graph.maxbucket
        ):  # Break from upper buckets if top bucket has been reached.
            if uf_plot is not None:
                pr.printlog("Max bucket number reached.")
                uf_plot.waitforkeypress() if plot else input()
            break

        if bucket == []:
            continue

        while bucket != []:  # Loop over all clusters in the current bucket\
            cluster = bucket.pop()
            root_cluster = find_cluster_root(cluster)
            if (
                root_cluster.bucket == bucket_i
            ):  # Check that cluster is not already in a higher bucket
                grow(
                    graph,
                    root_cluster,
                    root_cluster,
                    root_cluster.support,
                    uf_plot,
                    plot_step,
                    random_traverse,
                    vcomb,
                )
        if plot and not plot_step:
            uf_plot.draw_plot(
                "Growing bucket #" + str(bucket_i) + "/" + str(graph.maxbucket) + "."
            )
    if plot:
        pr.printlog("Clusters grown.")
        uf_plot.waitforkeypress()


def grow_full(
    graph,
    cluster,
    root_cluster,
    support,
    uf_plot=None,
    plot_step=0,
    print_steps=0,
    intervention=0,
    random_traverse=0,
    vcomb=0,
    family_growth=1,
):

    plot = True if uf_plot is not None else False
    root_level = (
        True if cluster == root_cluster else False
    )  # Check for root at beginning
    string = str(cluster) + " grown."
    merge_cluster = None

    if cluster.childs[1] != [] and print_steps:
        pr.printlog(f"{cluster} has fosters: {cluster.childs[1]}")

    while cluster.childs[1] != []:
        foster_cluster = cluster.childs[1].pop()
        grow_full(
            graph,
            foster_cluster,
            root_cluster,
            support,
            uf_plot,
            plot_step,
            print_steps,
            1,
            random_traverse,
            vcomb,
            0,
        )

    if family_growth:
        if cluster.childs[0] != [] and print_steps:
            pr.printlog(f"{cluster} has children: {cluster.childs[0]}")
        while cluster.childs[0] != []:  # First go through child clusters
            child_cluster = cluster.childs[0].pop()
            grow_full(
                graph,
                child_cluster,
                root_cluster,
                support,
                uf_plot,
                plot_step,
                print_steps,
                intervention,
                random_traverse,
                vcomb,
                1,
            )

    # cluster.boundary[0].reverse() if support == 0 else None
    while cluster.boundary[support] != []:
        root_cluster = find_cluster_root(cluster)
        (base_vertex, edge, grow_vertex) = cluster.boundary[support].pop()
        grow_cluster = grow_vertex.cluster
        grrt_cluster = find_cluster_root(grow_cluster)
        if grrt_cluster is None:  # if new_vertex has no cluster: add to cluster
            edge.support += 1
            if support:
                root_cluster.add_vertex(grow_vertex)
                edge.clsuter = root_cluster
                cluster_new_vertex(
                    graph, root_cluster, grow_vertex, random_traverse=random_traverse
                )
            else:
                root_cluster.boundary[1].append((base_vertex, edge, grow_vertex))
            if plot:
                uf_plot.add_edge(edge, base_vertex)
        elif (
            grrt_cluster is not root_cluster
        ):  # if new_vertex is from another cluster: union
            edge.support += 1
            if not support and edge.support == 2 or support:
                string += " Merged with " + str(grrt_cluster) + "."
                edge.cluster = grrt_cluster
                union_clusters(grrt_cluster, root_cluster)
                grrt_cluster.childs[0].append(root_cluster)
                merge_cluster = grrt_cluster
                if plot:
                    uf_plot.add_edge(edge, base_vertex)
                if intervention and family_growth and grrt_cluster.parity % 2 == 0:
                    grrt_cluster.childs[1].append(root_cluster)
                    if print_steps:
                        pr.printlog("intervention on merge.")
                    break
            elif not support:
                root_cluster.boundary[1].append((base_vertex, edge, grow_vertex))
                if plot:
                    uf_plot.add_edge(edge, base_vertex)
        else:
            None

    if family_growth:
        cluster.support = 1 - support

    if root_level:  # only at the root level will a cluster be placed in a new bucket
        if merge_cluster is None:
            cluster_place_bucket(graph, root_cluster, vcomb)
        else:
            cluster_place_bucket(graph, merge_cluster, vcomb)

    if plot and plot_step:
        uf_plot.draw_plot(string)
    if print_steps and root_level:
        if not plot:
            pr.printlog(string)
        print_cluster = root_cluster if merge_cluster is None else merge_cluster
        pr.print_graph(graph, [print_cluster], prestring="A: ", poststring="")
        if plot and plot_step:
            uf_plot.waitforkeypress()


def grow_clusters_full(
    graph,
    uf_plot=None,
    plot_step=0,
    print_steps=0,
    vcomb=0,
    random_traverse=0,
    intervention=0,
):

    plot = True if uf_plot is not None else False

    if print_steps:
        pr.print_graph(graph)
        uf_plot.waitforkeypress() if plot else input("Press any key to continue...")

    for bucket_i, bucket in enumerate(graph.buckets):

        if (
            bucket_i > graph.maxbucket
        ):  # Break from upper buckets if top bucket has been reached.
            if uf_plot is not None or print_steps:
                pr.printlog("Max bucket number reached.")
                uf_plot.waitforkeypress() if plot else input()
            break

        if bucket == []:
            continue

        if print_steps:
            pr.printlog(
                "\n############################ GROW ############################" + f"\nGrowing bucket {bucket_i} of {graph.maxbucket}: {bucket}" + f"\nRemaining buckets: {graph.buckets[bucket_i + 1 : graph.maxbucket + 1]}, {graph.wastebasket}\n"
            )
            uf_plot.waitforkeypress() if plot else input(
                "Press any key to continue...\n"
            )

        while bucket != []:  # Loop over all clusters in the current bucket
            cluster = bucket.pop()
            root_cluster = find_cluster_root(cluster)
            # if root_cluster is cluster:                                 # Check that cluster is at root
            if (
                root_cluster.bucket == bucket_i
            ):  # Check that cluster is not already in a higher bucket
                if print_steps:
                    pr.print_graph(graph, [root_cluster], prestring="B: ")
                grow_full(
                    graph,
                    root_cluster,
                    root_cluster,
                    root_cluster.support,
                    uf_plot,
                    plot_step,
                    print_steps,
                    intervention,
                    random_traverse,
                    vcomb,
                    1,
                )
            else:
                if print_steps:
                    if root_cluster.bucket is None:
                        pr.printlog(f"{root_cluster} is even.\n")
                    else:
                        if root_cluster.bucket > graph.maxbucket:
                            pr.printlog(f"{root_cluster} is already in the wastebasket\n")
                        else:
                            pr.printlog(f"{root_cluster} is already in another bucket.\n")

        if print_steps:
            pr.print_graph(graph, printmerged=0)

        if plot and not plot_step:
            txt = (
                ""
                if print_steps
                else "Growing bucket #"
                + str(bucket_i)
                + "/"
                + str(graph.maxbucket)
                + "."
            )
            uf_plot.draw_plot(txt)
    if plot:
        if print_steps:
            pr.print_graph(graph)
        if plot_step:
            pr.printlog("Clusters grown.")
            uf_plot.waitforkeypress()
