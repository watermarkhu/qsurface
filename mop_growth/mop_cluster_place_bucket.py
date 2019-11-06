def cluster_place_bucket(graph, cluster):
    """
    :param cluster      current cluster

    The inputted cluster has undergone a size change, either due to cluster growth or during a cluster merge, in which case the new root cluster is inputted. We increase the appropiate bucket number of the cluster intil the fitting bucket has been reached. The cluster is then appended to that bucket.
    If the max bucket number has been reached. The cluster is appended to the wastebasket, which will never be selected for growth.
    """

    def mop_growth_HG(size):
        if size == 1:
            return 5
        else:
            K = (-3 / 4 + (9 / 16 + (size - 2) / 2) ** (1 / 2)) // 1
            PG = 6 + 2 * K ** 2 + 7 * K
            id = (size - 2) - 2 * K ** 2 - 3 * K
            if id < K + 1:
                CG = 2
            elif id < 2 * (K + 1):
                CG = 3
            elif id < 3 * (K + 1) + 1:
                CG = 4
            else:
                CG = 5
            return int(PG + id + CG + size - 1)

    def mop_growth_FG(size):
        if size < 5:
            return size
        elif size < 8:
            return size + 1
        else:
            K = int(-7 / 4 + (49 / 16 + (size - 8) / 2) ** (1 / 2)) // 1
            PG = 2 * K ** 2 + 3 * K + 1
            base_bucket = mop_growth_HG(PG + 1)
            id = size - base_bucket + PG
            if id < K + 1:
                CG = id
            elif id < 2 * (K + 1) + 1:
                CG = id - 1
            elif id < 3 * (K + 1) + 3:
                CG = id - 2
            elif id < 4 * (K + 1) + 4:
                CG = id - 3
            else:
                CG = id - 4
            return int(base_bucket + id + CG + 1)

    if cluster.support:
        cluster.bucket = mop_growth_HG(cluster.size) - 1
    else:
        cluster.bucket = mop_growth_FG(cluster.size) - 1

    if cluster.parity % 2 == 1 and cluster.bucket < graph.numbuckets:
        graph.buckets[cluster.bucket].append(cluster)
        if cluster.bucket > graph.maxbucket:
            graph.maxbucket = cluster.bucket
    else:
        cluster.bucket = None
