import printing as pr
import random


def find_cluster_root(cluster):
    """
    :param cluster      input cluster

    Loops through the cluster tree to find the root cluster of the given cluster. When the parent cluster is not at the root level, the function is started again on the parent cluster. The recursiveness of the function makes sure that at each level the parent is pointed towards the root cluster, furfilling the collapsing rule.
    """
    if cluster is not None:
        if (
            cluster is not cluster.parent
            and cluster.parent is not cluster.parent.parent
        ):
            cluster.parent = find_cluster_root(cluster.parent)
        return cluster.parent
    else:
        return None


def union_clusters(parent, child):
    """
    :param parent       parent cluster
    :param child        child cluster

    Merges two clusters by updating the parent/child relationship and updating the attributes
    """
    child.parent = parent
    parent.size += child.size
    parent.parity += child.parity


def cluster_place_bucket(graph, cluster, vcomb=0):
    """
    :param cluster      current cluster

    The inputted cluster has undergone a size change, either due to cluster growth or during a cluster merge, in which case the new root cluster is inputted. We increase the appropiate bucket number of the cluster intil the fitting bucket has been reached. The cluster is then appended to that bucket.
    If the max bucket number has been reached. The cluster is appended to the wastebasket, which will never be selected for growth.
        """

    cluster.bucket = (
        cluster.size - 1 + cluster.support
        if vcomb
        else 2 * (cluster.size - 1) + cluster.support
    )

    if cluster.parity % 2 == 1 and cluster.bucket < graph.numbuckets:
        graph.buckets[cluster.bucket].append(cluster)
        if cluster.bucket > graph.maxbucket:
            graph.maxbucket = cluster.bucket
    else:
        cluster.bucket = None


class cluster_farmer:

    def __init__(
            self,
            graph,
            uf_plot=None,
            plot_growth=0,
            print_steps=0,
            random_order=0,
            random_traverse=0,
            intervention=0,
            vcomb=0
        ):
        self.graph = graph
        self.uf_plot = uf_plot
        self.plot_growth= plot_growth
        self.print_steps = print_steps
        self.random_order = random_order
        self.random_traverse = random_traverse
        self.intervention = intervention
        self.vcomb = vcomb
        self.plot = True if uf_plot is not None else False


    def cluster_new_vertex(self, cluster, vertex, plot_step=0):
        """
        :param cluster          current cluster
        :param vertex           vertex that is recently added to the cluster

        Recursive function which adds all connected erasure edges to a cluster, or finds the boundary on a vertex.

        For a given vertex, this function finds the neighboring edges and vertices that are in the the currunt cluster. Any new vertex or edge will be added to the graph.
        If the newly found edge is part of the erasure, the edge and the corresponding vertex will be added to the cluster, and the function is started again on the new vertex. Otherwise it will be added to the boundary.
        If a vertex is an anyon, its property and the parity of the cluster will be updated accordingly.
        """

        traverse_wind = random.sample(self.graph.wind, 4) if self.random_traverse else self.graph.wind

        for wind in traverse_wind:
            if wind in vertex.neighbors:
                (new_vertex, new_edge) = vertex.neighbors[wind]

                if new_edge.erasure:
                    if (
                        new_edge.support == 0 and not new_edge.peeled
                    ):  # if edge not already traversed
                        if new_vertex.cluster is None:  # if no cycle detected
                            new_edge.support = 2
                            cluster.add_vertex(new_vertex)
                            if self.plot and plot_step:
                                self.uf_plot.plot_edge_step(new_edge, "confirm")
                            self.cluster_new_vertex(cluster, vertex, plot_step)
                        else:  # cycle detected, peel edge
                            new_edge.peeled = True
                            if self.plot and plot_step:
                                self.uf_plot.plot_edge_step(new_edge, "remove")
                else:
                    if (
                        new_vertex.cluster is not cluster
                    ):  # Make sure new bound does not lead to self
                        cluster.boundary[0].append((vertex, new_edge, new_vertex))

    ##################  tree grown functions ####################

    def tree_grow(self, cluster, root_cluster, support):
        """
        :param cluster          the current cluster selected for growth
        :param root_cluster     the root cluster of the selected cluster

        Recursive function which first grows a cluster's children and then itself.

        There are two distinct growth steps. 1) first half step from a given vertex, the cluster size does not increase, no new edges or vertices are added to the cluster, except for during a merge. 2) second half step in which a new vertex is reached, and the edge is added to the cluster.
        During the inital {find_clusters} function, the initial boundary, which contains edges ready for growth step 1, are added to {full_bound}. {half_bound} which contains the boundary edges for growth step 2, is yet empty. From here, clusters from even buckets go into growth step 1 on edges from {full_bound}, and clusters from uneven buckets go into growth step 2 on edges from "half_bound". New boundary edges are added to the other boundary list.
        After growth, the cluster is placed into a new bucket using {cluster_place_bucket}. If a merge happens, the root cluster of the current cluster is made a child of the pendant root_cluster. And the pendant root cluster is placed in a new bucket instead.
        If a cluster has children, these clusters are grown first. The new boundaries from these child clusters are appended to the root_cluster. Such that a parent does not need to remember its children.
        """
        # Check for root at beginning
        root_level = True if cluster == root_cluster else False
        string = str(cluster) + " grown."
        merge_cluster = None

        while cluster.childs[0]:  # First go through child clusters
            child_cluster = cluster.childs[0].pop()
            self.tree_grow(child_cluster, root_cluster, support)

        # cluster.boundary[0].reverse() if support == 0 else None
        while cluster.boundary[support]:
            root_cluster = find_cluster_root(cluster)
            (base_vertex, edge, grow_vertex) = cluster.boundary[support].pop()
            grow_cluster = grow_vertex.cluster
            grrt_cluster = find_cluster_root(grow_cluster)
            if grrt_cluster is None:  # if new_vertex has no cluster: add to cluster
                edge.support += 1
                if support:
                    root_cluster.add_vertex(grow_vertex)
                    edge.cluster = root_cluster
                    self.cluster_new_vertex(root_cluster, grow_vertex, self.plot_growth)
                else:
                    root_cluster.boundary[1].append((base_vertex, edge, grow_vertex))
                if self.plot:
                    self.uf_plot.add_edge(edge, base_vertex)
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
                    if self.plot:
                        self.uf_plot.add_edge(edge, base_vertex)
                elif not support:
                    root_cluster.boundary[1].append((base_vertex, edge, grow_vertex))
                    if self.plot:
                        self.uf_plot.add_edge(edge, base_vertex)
            else:  # if new_vertex is in same cluster: nothing
                None

        cluster.support = 1 - support

        if root_level:  # only at the root level will a cluster be placed in a new bucket
            if merge_cluster is None:
                cluster_place_bucket(self.graph, root_cluster, self.vcomb)
            else:
                cluster_place_bucket(self.graph, merge_cluster, self.vcomb)

        if self.plot and self.plot_growth:
            self.uf_plot.draw_plot(string)


    def tree_grow_bucket(self, bucket, bucket_i):
        """
        Grows the current bucket. Only clusters with the same bucket_number are grown.
        """

        while bucket:  # Loop over all clusters in the current bucket\
            cluster = find_cluster_root(bucket.pop())

            # Check that cluster is not already in a higher bucket
            if cluster.bucket == bucket_i:
                self.tree_grow(cluster, cluster, cluster.support)


    ############ tree_full mehod, includes intervention and more printing ##########


    def tree_grow_full(self, cluster, root_cluster, support, family_growth=1):

        root_level = True if cluster == root_cluster else False
        string = str(cluster) + " grown."
        merge_cluster = None

        if cluster.childs[1] and self.print_steps:
            pr.printlog(f"{cluster} has fosters: {cluster.childs[1]}")

        while cluster.childs[1]:
            foster_cluster = cluster.childs[1].pop()
            self.tree_grow_full(foster_cluster, root_cluster, support, 0)

        if family_growth:
            if cluster.childs[0] and self.print_steps:
                pr.printlog(f"{cluster} has children: {cluster.childs[0]}")
            while cluster.childs[0]:  # First go through child clusters
                child_cluster = cluster.childs[0].pop()
                self.tree_grow_full(child_cluster, root_cluster, support, 1)

        # cluster.boundary[0].reverse() if support == 0 else None
        while cluster.boundary[support]:
            root_cluster = find_cluster_root(cluster)
            (base_vertex, edge, grow_vertex) = cluster.boundary[support].pop()
            grow_cluster = grow_vertex.cluster
            grrt_cluster = find_cluster_root(grow_cluster)
            if grrt_cluster is None:  # if new_vertex has no cluster: add to cluster
                edge.support += 1
                if support:
                    root_cluster.add_vertex(grow_vertex)
                    edge.cluster = root_cluster
                    self.cluster_new_vertex(root_cluster, grow_vertex, self.plot_growth)
                else:
                    root_cluster.boundary[1].append((base_vertex, edge, grow_vertex))
                if self.plot:
                    self.uf_plot.add_edge(edge, base_vertex)
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
                    if self.plot:
                        self.uf_plot.add_edge(edge, base_vertex)
                    if self.intervention and family_growth and grrt_cluster.parity % 2 == 0:
                        grrt_cluster.childs[1].append(root_cluster)
                        if self.print_steps:
                            pr.printlog("intervention on merge.")
                        break
                elif not support:
                    root_cluster.boundary[1].append((base_vertex, edge, grow_vertex))
                    if self.plot:
                        self.uf_plot.add_edge(edge, base_vertex)
            else:
                None

        if family_growth:
            cluster.support = 1 - support

        if root_level:  # only at the root level will a cluster be placed in a new bucket
            if merge_cluster is None:
                cluster_place_bucket(self.graph, root_cluster, self.vcomb)
            else:
                cluster_place_bucket(self.graph, merge_cluster, self.vcomb)

        if self.plot and self.plot_growth:
            self.uf_plot.draw_plot(string)
        if self.print_steps and root_level:
            if not self.plot:
                pr.printlog(string)
            print_cluster = root_cluster if merge_cluster is None else merge_cluster
            pr.print_graph(self.graph, [print_cluster], prestring="A: ", poststring="")
            if self.plot and self.plot_growth:
                self.uf_plot.waitforkeypress()



    def tree_grow_bucket_full(self, bucket, bucket_i):

        """
        Grows the current bucket. Only clusters with the same bucket_number are grown.
        """

        while bucket:  # Loop over all clusters in the current bucket
            cluster = find_cluster_root(bucket.pop())
            if cluster.bucket == bucket_i:
            # Check that cluster is not already in a higher bucket
                if self.print_steps:
                    pr.print_graph(self.graph, [cluster], prestring="B: ")
                self.tree_grow_full(cluster, cluster, cluster.support, 1)
            else:
                if self.print_steps:
                    if cluster.bucket is None:
                        pr.printlog(f"{cluster} is even.\n")
                    else:
                        if cluster.bucket > self.graph.maxbucket:
                            pr.printlog(f"{cluster} is already in the wastebasket\n")
                        else:
                            pr.printlog(f"{cluster} is already in another bucket.\n")

    #################################################################################
    ####### List unionfind method ########


    def list_grow_bucket(self, bucket, bucket_i):

        fusion, place = [], []  # Initiate Fusion list

        while bucket:  # Loop over all clusters in the current bucket\
            cluster = find_cluster_root(bucket.pop())

            if cluster.bucket == bucket_i and cluster.support == bucket_i % 2:
                # Check that cluster is not already in a higher bucket
                place.append(cluster)

                # Set boudary
                cluster.boundary = [[], cluster.boundary[0]]

                # Grow cluster support for bucket placement
                cluster.support = 1 - cluster.support

                # for vertex, new_edge, new_vertex in cluster.boundary[1]:
                while cluster.boundary[1]:
                    vertex, new_edge, new_vertex = cluster.boundary[1].pop()

                    # Grow boundaries by half-edge
                    if new_edge.support != 2:
                        new_edge.support += 1
                        if new_edge.support == 2:
                            # Apped to fusion list of edge fully grown
                            fusion.append((vertex, new_edge, new_vertex))
                        else:
                            # Half grown edges are added immediately to new boundary
                            cluster.boundary[0].append((vertex, new_edge, new_vertex))
                        if self.plot: self.uf_plot.add_edge(new_edge, vertex)
                if self.plot_growth: self.uf_plot.draw_plot(str(cluster) + " grown.")

        if self.print_steps: mstr = {}
        for base_vertex, edge, grow_vertex in fusion:
            base_cluster = find_cluster_root(base_vertex.cluster)
            grow_cluster = find_cluster_root(grow_vertex.cluster)
            if grow_cluster is None:
                # Fully grown edge. New vertex is on the old boundary. Find new boundary on vertex
                base_cluster.add_vertex(grow_vertex)
                self.cluster_new_vertex(base_cluster, grow_vertex, self.plot_growth)
            elif grow_cluster is base_cluster:
                # Edge grown on itself. This cluster is already connected. Cut half-edge
                edge.support -= 1
                if self.plot: self.uf_plot.add_edge(edge, base_vertex)
            else:  # Clusters merge by weighted union
                if grow_cluster.size < base_cluster.size:  # apply weighted union
                    base_cluster, grow_cluster = grow_cluster, base_cluster
                if self.print_steps:  # Keep track of which clusters are merged into one
                    if base_cluster.cID not in mstr:
                        mstr[base_cluster.cID] = pr.print_graph(self.graph, [base_cluster], return_string=True)
                    if grow_cluster.cID not in mstr:
                        mstr[grow_cluster.cID] = pr.print_graph(self.graph, [grow_cluster], return_string=True)
                    mstr[grow_cluster.cID] += "\n" + mstr[base_cluster.cID]
                    mstr.pop(base_cluster.cID)
                union_clusters(grow_cluster, base_cluster)
                grow_cluster.boundary[0].extend(base_cluster.boundary[0])
        if self.print_steps:
            pr.printlog("")
            for cID, string in mstr.items():
                pr.printlog(f"B:\n{string}\nA:\n{pr.print_graph(self.graph, [self.graph.C[cID]], return_string=True)}\n")

        # Put clusters in new buckets. Some will be added double, but will be skipped by the new_boundary check
        for cluster in place:
            cluster = find_cluster_root(cluster)
            cluster_place_bucket(self.graph, cluster)

        if self.plot and not self.plot_growth:
            self.uf_plot.draw_plot("Clusters merged")


    ######################## General functions #############################


    def grow_clusters(self, method="list", start_bucket=0):

        grow_bucket = {
            "tree": self.tree_grow_bucket,
            "tree_full": self.tree_grow_bucket_full,
            "list": self.list_grow_bucket
        }

        if self.print_steps:
            pr.print_graph(self.graph)
            self.uf_plot.waitforkeypress() if self.plot else input("Press any key to continue...")

        for bucket_i, bucket in enumerate(self.graph.buckets[start_bucket:], start_bucket):

            if bucket_i > self.graph.maxbucket:
                # Break from upper buckets if top bucket has been reached.
                if self.uf_plot is not None or self.print_steps:
                    pr.printlog("Max bucket number reached.")
                    self.uf_plot.waitforkeypress() if self.plot else input()
                break

            if not bucket:  # no need to check empty bucket
                continue

            if self.print_steps:
                pr.printlog(
                "\n############################ GROW ############################" + f"\nGrowing bucket {bucket_i} of {self.graph.maxbucket}: {bucket}" + f"\nRemaining buckets: {self.graph.buckets[bucket_i + 1 : self.graph.maxbucket + 1]}, {self.graph.wastebasket}\n"
                )
                self.uf_plot.waitforkeypress()

            grow_bucket[method](bucket, bucket_i)

            if self.print_steps:
                pr.print_graph(self.graph, printmerged=0)

            if self.plot:
                self.uf_plot.ax.set_xlabel("")
                if not self.plot_growth and not self.print_steps:
                    txt = "" if self.print_steps else f"Growing bucket #{bucket_i}/{self.graph.maxbucket}"
                    self.uf_plot.draw_plot(txt)

        if self.plot:
            if self.print_steps:
                pr.print_graph(self.graph)
            if self.plot_growth:
                pr.printlog("Clusters grown.")
                self.uf_plot.waitforkeypress()


    def find_clusters(self, order="Vup-Hup", plot_step=0):
        """
        Given a set of erased qubits/edges on a lattice, this functions finds all edges that are connected and sorts them in separate clusters. A single anyon can also be its own cluster.
        It loops over all vertices (randomly if toggled, which produces a different tree), and calls {cluster_new_vertex} to find all connected erasure qubits, and finds the boundary for growth step 1. Afterwards the cluster is placed in a bucket based in its size.

        """
        self.graph.numbuckets = self.graph.size * (self.graph.size // 2 - 1) * 2
        self.graph.buckets = [[] for _ in range(self.graph.numbuckets)]
        self.graph.wastebasket = []
        self.graph.maxbucket = 0

        cID, s = 0, self.graph.size

        if order == "Vup-Hup":
            vertices = self.graph.V.values()
        if order == "Vdo-Hdo":
            vertices = [self.graph.V[(t, y, x)]
                for x in reversed(range(s))
                for y in reversed(range(s))
                for t in range(2)
                ]
        elif order == "Hup-Vdo":
            vertices = [self.graph.V[(t, y, x)]
                for y in reversed(range(s))
                for x in range(s)
                for t in range(2)
                ]
        elif order == "Hdo-Vdo":
            vertices = [self.graph.V[(t, y, x)]
                for y in reversed(range(s))
                for x in reversed(range(s))
                for t in range(2)
                ]
        elif order == "random":
            vertices = random.sample(list(self.graph.V.values()), s*s*2)

        anyons = [vertex for vertex in vertices if vertex.state]

        for vertex in anyons:
            if vertex.cluster is None:
                cluster = self.graph.add_cluster(cID)
                cluster.add_vertex(vertex)
                self.cluster_new_vertex(cluster, vertex, plot_step)
                cluster_place_bucket(self.graph, cluster, self.vcomb)
                cID += 1

        if self.uf_plot is not None and not plot_step:
            self.uf_plot.plot_removed(self.graph, "Clusters initiated.")
        elif self.uf_plot is not None:
            self.uf_plot.waitforkeypress("Clusters initiated.")


    def peel_clusters(self, plot_step=0):
        """
        Loops overal all vertices to find pendant vertices which are selected from peeling using {peel_edge}

        """

        def peel_edge(cluster, vertex):
            """
            :param cluster          current active cluster
            :param vertex           pendant vertex of the edge to be peeled

            Recursive function which peels a branch of the tree if the input vertex is a pendant vertex

            If there is only one neighbor of the input vertex that is in the same cluster, this vertex is a pendant vertex and can be peeled. The function calls itself on the other vertex of the edge leaf.
            """
            plot = True if self.plot and plot_step else False
            num_connect = 0

            for wind in self.graph.wind:
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
                    edge.state = not edge.state
                    edge.matching = True
                    vertex.state = False
                    new_vertex.state = not new_vertex.state
                    if plot:
                        self.uf_plot.plot_edge_step(edge, "match")
                        self.uf_plot.plot_strip_step_anyon(vertex)
                        self.uf_plot.plot_strip_step_anyon(new_vertex)
                else:
                    if plot:
                        self.uf_plot.plot_edge_step(edge, "peel")
                peel_edge(cluster, new_vertex)

        for vertex in self.graph.V.values():
            if vertex.cluster is not None:
                cluster = find_cluster_root(vertex.cluster)
                peel_edge(cluster, vertex)

        if self.plot and not plot_step:
            self.uf_plot.plot_removed(self.graph, "Peeling completed.")
