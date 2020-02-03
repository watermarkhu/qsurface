import plot_unionfind as up
import printing as pr
import random


class toric(object):

    def __init__(
            self,
            graph,
            plot_config=None,
            **kwargs
        ):
        self.graph = graph
        self.plot_config = plot_config

        for key, value in kwargs.items():
            setattr(self, key, value)


    def decode(self):


        self.plot = up.unionfind_plot(self.graph, **self.plot_config) if self.graph.plot else None

        self.find_clusters()
        self.grow_clusters()
        self.peel_clusters()

    '''
    ##################################################################################################

                                            UNION-FIND funtions

    ##################################################################################################
    '''

    def union_clusters(self, parent, child):
        """
        :param parent       parent cluster
        :param child        child cluster

        Merges two clusters by updating the parent/child relationship and updating the attributes
        """
        child.parent = parent
        parent.size += child.size
        parent.parity += child.parity


    def find_cluster_root(self, cluster):
        """
        :param cluster      input cluster

        Loops through the cluster tree to find the root cluster of the given cluster. When the parent cluster is not at the root level, the function is started again on the parent cluster. The recursiveness of the function makes sure that at each level the parent is pointed towards the root cluster, furfilling the collapsing rule.
        """
        if cluster is not None:
            if (
                cluster is not cluster.parent
                and cluster.parent is not cluster.parent.parent
            ):
                cluster.parent = self.find_cluster_root(cluster.parent)
            return cluster.parent
        else:
            return None

    '''
    ##################################################################################################

                                        General helper funtions

    ##################################################################################################
    '''

    def cluster_place_bucket(self, cluster):
        """
        :param cluster      current cluster

        The inputted cluster has undergone a size change, either due to cluster growth or during a cluster merge, in which case the new root cluster is inputted. We increase the appropiate bucket number of the cluster intil the fitting bucket has been reached. The cluster is then appended to that bucket.
        If the max bucket number has been reached. The cluster is appended to the wastebasket, which will never be selected for growth.
            """

        cluster.bucket = 2 * (cluster.size - 1) + cluster.support

        if (cluster.parity % 2 == 1 and not cluster.on_bound) and cluster.bucket < self.graph.numbuckets:
            self.graph.buckets[cluster.bucket].append(cluster)
            if cluster.bucket > self.graph.maxbucket:
                self.graph.maxbucket = cluster.bucket
        else:
            cluster.bucket = None


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

                if new_edge.qubit.erasure:
                    # if edge not already traversed
                    if new_edge.support == 0 and not new_edge.peeled:
                        if new_vertex.cluster is None:  # if no cycle detected
                            new_edge.support = 2
                            cluster.add_vertex(new_vertex)
                            if self.graph.plot and plot_step:
                                self.plot.plot_edge_step(new_edge, "confirm")
                            self.cluster_new_vertex(cluster, new_vertex, plot_step)
                        else:  # cycle detected, peel edge
                            new_edge.peeled = True
                            if self.graph.plot and plot_step:
                                self.plot.plot_edge_step(new_edge, "remove")
                else:
                    # Make sure new bound does not lead to self
                    if new_vertex.cluster is not cluster:
                        cluster.boundary[0].append((vertex, new_edge, new_vertex))

    '''
    ##################################################################################################

                                            1. Find clusters

    ##################################################################################################
    '''
    def find_clusters(self):
        """
        Given a set of erased qubits/edges on a lattice, this functions finds all edges that are connected and sorts them in separate clusters. A single anyon can also be its own cluster.
        It loops over all vertices (randomly if toggled, which produces a different tree), and calls {cluster_new_vertex} to find all connected erasure qubits, and finds the boundary for growth step 1. Afterwards the cluster is placed in a bucket based in its size.

        """
        self.graph.numbuckets = self.graph.size * (self.graph.size // 2 - 1) * 2
        self.graph.buckets = [[] for _ in range(self.graph.numbuckets)]
        self.graph.wastebasket = []
        self.graph.maxbucket = 0


        vertices = self.graph.S.values()
        anyons = [vertex for vertex in vertices if vertex.state]

        for vertex in anyons:
            if vertex.cluster is None:
                cluster = self.graph.add_cluster(self.graph.cID, vertex)
                self.cluster_new_vertex(cluster, vertex, self.plot_find)
                self.cluster_place_bucket(cluster)
                self.graph.cID += 1

        if self.plot is not None:
            if not self.plot_find:
                self.plot.plot_removed()
            self.plot.draw_plot("Clusters initiated.")

    '''
    ##################################################################################################

                                            2(a). Grow clusters expand

                                            top:    grow_clusters
                                            mid:    grow_bucket
                                            bot:    grow_boundary

    ##################################################################################################
    '''

    def grow_clusters(self, start_bucket=0):

        if self.print_steps:
            pr.print_graph(self.graph)
            self.plot.waitforkeypress() if self.graph.plot else input("Press any key to continue...")

        for bucket_i, bucket in enumerate(self.graph.buckets[start_bucket:], start_bucket):

            if bucket_i > self.graph.maxbucket:
                # Break from upper buckets if top bucket has been reached.
                if self.plot is not None or self.print_steps:
                    pr.printlog("Max bucket number reached.")
                    self.plot.waitforkeypress() if self.graph.plot else input()
                break

            if not bucket:  # no need to check empty bucket
                continue

            if self.print_steps:
                pr.printlog(
                "\n############################ GROW ############################" + f"\nGrowing bucket {bucket_i} of {self.graph.maxbucket}: {bucket}" + f"\nRemaining buckets: {self.graph.buckets[bucket_i + 1 : self.graph.maxbucket + 1]}, {self.graph.wastebasket}\n"
                )
                self.plot.waitforkeypress()

            self.grow_bucket(bucket, bucket_i)

            if self.print_steps:
                pr.print_graph(self.graph, printmerged=0)

            if self.graph.plot:
                self.plot.ax.set_xlabel("")
                if not self.plot_growth and not self.print_steps:
                    txt = "" if self.print_steps else f"Growing bucket #{bucket_i}/{self.graph.maxbucket}"
                    self.plot.draw_plot(txt)

        if self.graph.plot:
            if self.print_steps:
                pr.print_graph(self.graph, include_even=1)
            if self.plot_growth:
                self.plot.draw_plot("Clusters grown.")


    def grow_bucket(self, bucket, bucket_i):

        if self.print_steps: self.mstr = {}
        self.fusion, place = [], []  # Initiate Fusion list

        while bucket:  # Loop over all clusters in the current bucket\
            cluster = self.find_cluster_root(bucket.pop())

            if cluster.bucket == bucket_i and cluster.support == bucket_i % 2:
                place.append(cluster)
                cluster.support = 1 - cluster.support
                self.grow_boundary(cluster)

        self.fuse_vertices()
        # self.fuse_dgvertices()

        if self.print_steps:
            pr.printlog("")
            for cID, string in self.mstr.items():
                pr.printlog(f"B:\n{string}\nA:\n{pr.print_graph(self.graph, [self.graph.C[cID]], include_even=1, return_string=True)}\n")

        # Put clusters in new buckets. Some will be added double, but will be skipped by the new_boundary check
        for cluster in place:
            cluster = self.find_cluster_root(cluster)
            self.cluster_place_bucket(cluster)

        if self.graph.plot and not self.plot_growth:
            self.plot.draw_plot("Clusters merged")


    def grow_boundary(self, cluster):

        cluster.boundary = [[], cluster.boundary[0]]                # Set boudary

        while cluster.boundary[1]:                                  # grow boundary
            bound = cluster.boundary[1].pop()
            vertex, new_edge, new_vertex = bound

            if new_edge.support != 2:                           # if not already fully grown
                new_edge.support += 1                           # Grow boundaries by half-edge
                if new_edge.support == 2:                       # if edge is fully grown
                    self.fusion.append(bound)                   # Append to fusion list of edges
                else:
                    cluster.boundary[0].append(bound)

                if self.graph.plot: self.plot.add_edge(new_edge, vertex)

        if self.plot_growth: self.plot.draw_plot(str(cluster) + " grown.")

    '''
    ##################################################################################################

                                            2(b). Grow clusters fuse

    ##################################################################################################
    '''


    def fuse_vertices(self, ):
        for active_V, edge, passive_V in self.fusion:
            self.fully_grown_edge_choises(active_V, edge, passive_V)


    def fuse_dgvertices(self):

        merging = []
        for active_V, edge, passive_V in self.fusion:
            active_C = self.find_cluster_root(active_V.cluster)
            passive_C = self.find_cluster_root(passive_V.cluster)

            '''
            if:     Fully grown edge. New vertex is on the old boundary. Find new boundary on vertex
            elif:   Edge grown on itself. This cluster is already connected. Cut half-edge
            else:   Clusters merge by weighted union
            '''

            if passive_C is None:
                active_C.add_vertex(passive_V)
                self.cluster_new_vertex(active_C, passive_V, self.plot_growth)

            elif passive_C is active_C:
                edge.support -= 1
                if self.graph.plot: self.plot.add_edge(edge, active_V)

            else:
                merging.append((active_V, edge, passive_V))

        for active_V, edge, passive_V in merging:
            active_V.count += 1
            passive_V.count += 1

        merge_buckets = [[] for i in range(6)]
        for mergevertices in merging:
            (active_V, edge, passive_V) = mergevertices
            index = 7 - (active_V.count + passive_V.count)
            merge_buckets[index].append(mergevertices)

        for merge_bucket in merge_buckets:
            for active_V, edge, passive_V in merge_bucket:
                active_V.count, passive_V.count = 0, 0
                self.fully_grown_edge_choises(active_V, edge, passive_V)


    def fully_grown_edge_choises(self, active_V, edge, passive_V):

        active_C = self.find_cluster_root(active_V.cluster)
        passive_C = self.find_cluster_root(passive_V.cluster)

        '''
        if:     Fully grown edge. New vertex is on the old boundary. Find new boundary on vertex
        elif:   Edge grown on itself. This cluster is already connected. Cut half-edge
        else:   Clusters merge by weighted union
        '''

        if passive_C is None:
            active_C.add_vertex(passive_V)
            self.cluster_new_vertex(active_C, passive_V, self.plot_growth)

        elif passive_C is active_C:
            edge.support -= 1
            if self.graph.plot: self.plot.add_edge(edge, active_V)

        else:
            if passive_C.size < active_C.size:  # of clusters
                active_C, passive_C = passive_C, active_C
            if self.print_steps:                            # Keep track of which clusters are merged into one to print later
                if active_C.cID not in self.mstr:
                    self.mstr[active_C.cID] = pr.print_graph(self.graph, [active_C], return_string=True)
                if passive_C.cID not in self.mstr:
                    self.mstr[passive_C.cID] = pr.print_graph(self.graph, [passive_C], return_string=True)
                self.mstr[passive_C.cID] += "\n" + self.mstr[active_C.cID]
                self.mstr.pop(active_C.cID)
            self.union_clusters(passive_C, active_C)
            passive_C.boundary[0].extend(active_C.boundary[0])                      # Combine boundaries



    '''
    ##################################################################################################

                                            3. Peel clusters

    ##################################################################################################
    '''

    def peel_clusters(self):
        """
        Loops overal all vertices to find pendant vertices which are selected from peeling using {peel_edge}

        """
        for vertex in self.graph.S.values():
            if vertex.cluster is not None:
                cluster = self.find_cluster_root(vertex.cluster)
                self.peel_edge(cluster, vertex)

        if self.graph.plot and not self.plot_peel:
            self.plot.plot_removed()
            self.plot.draw_plot("Clusters peeled.")


    def peel_edge(self, cluster, vertex):
        """
        :param cluster          current active cluster
        :param vertex           pendant vertex of the edge to be peeled

        Recursive function which peels a branch of the tree if the input vertex is a pendant vertex

        If there is only one neighbor of the input vertex that is in the same cluster, this vertex is a pendant vertex and can be peeled. The function calls itself on the other vertex of the edge leaf.
        """
        plot = True if self.graph.plot and self.plot_peel else False
        num_connect = 0

        for (NV, NE) in vertex.neighbors.values():
            if NE.support == 2:
                new_cluster = self.find_cluster_root(NV.cluster)
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
                    self.plot.plot_edge_step(edge, "match")
                    self.plot.plot_strip_step_anyon(vertex)
                    if new_vertex.type == 0:
                        self.plot.plot_strip_step_anyon(new_vertex)
            else:
                if plot: self.plot.plot_edge_step(edge, "peel")
            self.peel_edge(cluster, new_vertex)


class planar(toric):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def decode(self):

        self.plot = up.unionfind_plot(self.graph, **self.plot_config) if self.graph.plot else None

        self.find_clusters_boundary()
        self.find_clusters()
        self.grow_clusters()
        self.peel_clusters()

    '''
    ##################################################################################################

                                            UNION-FIND funtions

    ##################################################################################################
    '''
    def union_clusters(self, parent, child):
        super().union_clusters(parent, child)
        parent.on_bound = parent.on_bound or child.on_bound

    '''
    ##################################################################################################

                                        General helper funtions

    ##################################################################################################
    '''

    def cluster_new_vertex(self, cluster, vertex, plot_step=0):

        if vertex.type == 1:
            cluster.on_bound = 1

        super().cluster_new_vertex(cluster, vertex, plot_step)

    '''
    ##################################################################################################

                                    0. Find clusters on boundary

    ##################################################################################################
    '''
    def find_clusters_boundary(self):

        self.graph.numbuckets = 0

        bound_clusters = []
        self.bound_cluster_vertices = []

        erasure_bound = []
        for bound in self.graph.B.values():
            for vertex, edge in bound.neighbors.values():
                if edge.qubit.erasure:
                    cluster = self.graph.get_cluster(self.graph.cID, bound)
                    cluster.on_bound = 1
                    bound_clusters.append(cluster)
                    self.bound_cluster_vertices.append([bound])
                    erasure_bound.append(bound)
                    self.graph.cID += 1

        self.bound_cluster_edges = [[] for _ in range(self.graph.cID)]
        self.cluster_new_vertex_boundary(erasure_bound)

        for cluster in bound_clusters:

            if cluster.parity == 0:
                for vertex in self.bound_cluster_vertices[cluster.cID]:
                    vertex.cluster = None
                for edge in self.bound_cluster_edges[cluster.cID]:
                    edge.support = 0
            else:
                self.graph.C[cluster.cID] = cluster
                self.cluster_place_bucket(cluster)


    def cluster_new_vertex_boundary(self, bound_list):

        if not bound_list:
            return

        new_list = []

        traverse_wind = random.sample(self.graph.wind, 4) if self.random_traverse else self.graph.wind

        for vertex in bound_list:
            for wind in traverse_wind:
                if wind in vertex.neighbors:
                    (new_vertex, new_edge) = vertex.neighbors[wind]

                    if new_edge.qubit.erasure:
                        # if edge not already traversed
                        if new_edge.support == 0 and not new_edge.peeled:
                            if new_vertex.cluster is None:  # if no cycle detected
                                new_edge.support = 2
                                vertex.cluster.add_vertex(new_vertex)
                                self.bound_cluster_edges[vertex.cluster.cID].append(new_edge)
                                self.bound_cluster_vertices[vertex.cluster.cID].append(new_vertex)
                                if self.graph.plot and self.plot_find:
                                    self.plot.plot_edge_step(new_edge, "confirm")
                                new_list.append(new_vertex)
                            else:  # cycle detected, peel edge
                                new_edge.peeled = True
                                if self.graph.plot and self.plot_find:
                                    self.plot.plot_edge_step(new_edge, "remove")
                    else:
                        # Make sure new bound does not lead to self
                        if new_vertex.cluster is not vertex.cluster:
                            vertex.cluster.boundary[0].append((vertex, new_edge, new_vertex))

        self.cluster_new_vertex_boundary(new_list)

    '''
    ##################################################################################################

                                            2(b). Grow clusters fuse

    ##################################################################################################
    '''


    def fully_grown_edge_choises(self, active_V, edge, passive_V):

        active_C = self.find_cluster_root(active_V.cluster)
        passive_C = self.find_cluster_root(passive_V.cluster)
        if active_C.on_bound and (passive_V.type == 1 or (passive_C is not None and passive_C.on_bound)):
            edge.support -= 1
            if self.graph.plot: self.plot.add_edge(edge, active_V)
        else:
            super().fully_grown_edge_choises(active_V, edge, passive_V)
