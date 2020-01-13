import printing as pr
import random
import evengrow as eg


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
                    if new_edge.support == 0 and not new_edge.peeled:
                        # if edge not already traversed
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
                    if new_vertex.cluster is not cluster:
                        # Make sure new bound does not lead to self
                        cluster.boundary[0].append((vertex, new_edge, new_vertex))


    #################################################################################
    ####### List unionfind method ########


    def list_grow_bucket(self, bucket, bucket_i):

        fusion, place, waited_nodes = [], [], [] # Initiate Fusion list

        while bucket:  # Loop over all clusters in the current bucket
            cluster = find_cluster_root(bucket.pop())

            if cluster.bucket == bucket_i and cluster.support == bucket_i % 2:

                if cluster.root_node.calc_delay and self.print_steps:
                    calc_nodes = [node.short_id for node in cluster.root_node.calc_delay]
                    print("Computing delay root {} at nodes {} and children".format(cluster.root_node.short_id, calc_nodes))
                    print_tree = True
                else:
                    print_tree = False

                while cluster.root_node.calc_delay:
                    node = cluster.root_node.calc_delay.pop()
                    eg.comp_tree_p_of_node(node)
                    eg.comp_tree_d_of_node(node, cluster)

                if print_tree:
                    pr.print_tree(cluster.root_node, "children", "tree_rep")

                place.append(cluster)

                # Set boudary
                cluster.boundary = [[], cluster.boundary[0]]

                # Grow cluster support for bucket placement
                cluster.support = 1 - cluster.support

                # for vertex, new_edge, new_vertex in cluster.boundary[1]:
                while cluster.boundary[1]:
                    bound = cluster.boundary[1].pop()
                    vertex, new_edge, new_vertex = bound

                    node = vertex.node

                    if node.d - node.w - cluster.mindl == 0:      # waited enough rounds as delay
                        waited = False

                        # Grow boundaries by half-edge
                        if new_edge.support != 2:
                            new_edge.support += 1

                            if new_edge.support == 2:                       # if edge is fully grown
                                fusion.append(bound)                        # Append to fusion list of edges
                            else:
                                cluster.boundary[0].append(bound)
                            if self.plot: self.uf_plot.add_edge(new_edge, vertex)
                    else:
                        waited = True
                        cluster.boundary[0].append(bound)

                    # grow node size if not done before in same bucket
                    if node.bucket != bucket_i:
                        node.bucket = bucket_i
                        node.s += 1
                        if waited:
                            waited_nodes.append(node)

                if self.plot_growth: self.uf_plot.draw_plot(str(cluster) + " grown.")

        for node in waited_nodes:
            node.w += 1

        if self.print_steps: mstr = {}
        for active_V, edge, passive_V in fusion:
            active_C = find_cluster_root(active_V.cluster)
            passive_C = find_cluster_root(passive_V.cluster)

            # Fully grown edge. New vertex is on the old boundary. Find new boundary on vertex
            if passive_C is None:
                active_C.add_vertex(passive_V)

                # TODO: add some part in cluster_new_vertex to solve for erasure errors.
                passive_V.node = active_V.node
                self.cluster_new_vertex(active_C, passive_V, self.plot_growth)

            # Edge grown on itself. This cluster is already connected. Cut half-edge
            elif passive_C is active_C:
                edge.support -= 1
                if self.plot: self.uf_plot.add_edge(edge, active_V)

            # Clusters merge by weighted union
            else:
                # Apply union of anyontrees
                root_node = eg.adoption(active_V, passive_V, active_C, passive_C)

                # Apply weighted union of cluster trees
                if passive_C.size < active_C.size:
                    active_C, passive_C = passive_C, active_C

                # Keep track of which clusters are merged into one to print later
                if self.print_steps:
                    if active_C.cID not in mstr:
                        mstr[active_C.cID] = pr.print_graph(self.graph, [active_C], return_string=True)
                    if passive_C.cID not in mstr:
                        mstr[passive_C.cID] = pr.print_graph(self.graph, [passive_C], return_string=True)
                    mstr[passive_C.cID] += "\n" + mstr[active_C.cID]
                    mstr.pop(active_C.cID)

                union_clusters(passive_C, active_C)

                # Append boundary of smaller cluster to larger cluster
                passive_C.boundary[0].extend(active_C.boundary[0])
                passive_C.root_node = root_node

        # Put clusters in new buckets. Some will be added double, but will be skipped by the new_boundary check
        for cluster in place:
            cluster = find_cluster_root(cluster)
            cluster_place_bucket(self.graph, cluster)

        if self.print_steps:
            pr.printlog("")
            for cID, string in mstr.items():
                pr.printlog(f"B:\n{string}\nA:\n{pr.print_graph(self.graph, [self.graph.C[cID]], return_string=True)}\n")

        if self.plot and not self.plot_growth:
            self.uf_plot.draw_plot("Clusters merged")


    ######################## General functions #############################


    def grow_clusters(self, method="list", start_bucket=0):

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
                "\n############################ GROW ############################" + f"\nGrowing bucket {bucket_i} of {self.graph.maxbucket}: {bucket}" + f"\nReactiveing buckets: {self.graph.buckets[bucket_i + 1 : self.graph.maxbucket + 1]}, {self.graph.wastebasket}\n"
                )
                self.uf_plot.waitforkeypress()

            self.list_grow_bucket(bucket, bucket_i)

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

        cID = 0
        vertices = self.graph.V.values()

        anyons = []
        for vertex in vertices:
            if vertex.state:
                anyons.append(vertex)
                vertex.node = eg.anyon_node(vertex.sID)

        for vertex in anyons:
            if vertex.cluster is None:
                cluster = self.graph.add_cluster(cID, vertex)
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
