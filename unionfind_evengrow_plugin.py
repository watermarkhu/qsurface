import unionfind as uf
import printing as pr
import evengrow_directed as eg


class toric(uf.toric):

    def cluster_new_vertex(self, cluster, vertex, plot_step=0, *args, **kwargs):
        """
        :param cluster          current cluster
        :param vertex           vertex that is recently added to the cluster

        Recursive function which adds all connected erasure edges to a cluster, or finds the boundary on a vertex.

        For a given vertex, this function finds the neighboring edges and vertices that are in the the currunt cluster. Any new vertex or edge will be added to the graph.
        If the newly found edge is part of the erasure, the edge and the corresponding vertex will be added to the cluster, and the function is started again on the new vertex. Otherwise it will be added to the boundary.
        If a vertex is an anyon, its property and the parity of the cluster will be updated accordingly.
        """

        for (new_vertex, new_edge) in vertex.neighbors.values():

            if new_edge.qubit.erasure:
                # if edge not already traversed
                if new_edge.support == 0 and not new_edge.peeled:
                    if new_vertex.cluster is None:  # if no cycle detected
                        new_edge.support = 2
                        cluster.add_vertex(new_vertex)
                        eg.new_empty(vertex, new_vertex, cluster)

                        if self.plot and plot_step:
                            self.plot.plot_edge_step(new_edge, "confirm")
                        self.cluster_new_vertex(cluster, new_vertex, plot_step)
                    else:  # cycle detected, peel edge
                        new_edge.peeled = True
                        if self.plot and plot_step:
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

    def find_clusters(self, *args, **kwargs):
        """
        Given a set of erased qubits/edges on a lattice, this functions finds all edges that are connected and sorts them in separate clusters. A single anyon can also be its own cluster.
        It loops over all vertices (randomly if toggled, which produces a different tree), and calls {cluster_new_vertex} to find all connected erasure qubits, and finds the boundary for growth step 1. Afterwards the cluster is placed in a bucket based in its size.

        """
        anyons = []
        for layer in self.graph.S.values():
            for vertex in layer.values():
                if vertex.state:
                    anyons.append(vertex)
                    vertex.node = eg.anyon_node(vertex)

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

    def grow_boundary(self, cluster, bucket_i, *args, **kwargs):

        if cluster.root_node.calc_delay and self.print_steps:
            calc_nodes = [node.short_id()
             for node in cluster.root_node.calc_delay]
            print("Computing delay root {} at nodes {} and children".format(cluster.root_node.short_id(), calc_nodes))
            print_tree = True
        else:
            print_tree = False

        while cluster.root_node.calc_delay:                         # calculate parity and delay in even part
            at_node = cluster.root_node.calc_delay.pop()
            eg.comp_tree_p_of_node(at_node)
            eg.comp_tree_d_of_node(at_node, cluster)

        if print_tree:
            pr.print_tree(cluster.root_node, "children", "tree_rep")

        cluster.boundary = [[], cluster.boundary[0]]                # Set boudary
        waited_nodes = []

        while cluster.boundary[1]:                                  # grow boundary
            bound = cluster.boundary[1].pop()
            vertex, new_edge, new_vertex = bound
            node = vertex.node

            if node.d - node.w == cluster.mindl:                    # waited enough rounds as delay
                waited = False

                if new_edge.support != 2:                           # if not already fully grown
                    new_edge.support += 1                           # Grow boundaries by half-edge
                    if new_edge.support == 2:                       # if edge is fully grown
                        self.fusion.append(bound)                   # Append to fusion list
                    else:
                        cluster.boundary[0].append(bound)

                    if self.plot: self.plot.add_edge(new_edge, vertex)
            else:
                waited = True
                cluster.boundary[0].append(bound)

            if node.bucket != bucket_i:                             # grow node size if not done before in same bucket
                node.bucket = bucket_i                              # Make sure this loop happens once per node
                if waited:
                    waited_nodes.append(node)
                else:
                    node.s += 1

        for node in waited_nodes:
            node.w += 1

    '''
    ##################################################################################################

                                            2(b). Grow clusters fuse

    ##################################################################################################
    '''

    def fuse_dgvertices(self, *args, **kwargs):

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
                passive_V.node = active_V.node
                self.cluster_new_vertex(active_C, passive_V, self.plot_growth)

            elif passive_C is active_C:
                edge.support -= 1
                if self.plot: self.plot.add_edge(edge, active_V)

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


    def fully_grown_edge_choises(self, active_V, edge, passive_V, *args, **kwargs):

        active_C = self.find_cluster_root(active_V.cluster)
        passive_C = self.find_cluster_root(passive_V.cluster)

        '''
        if:     Fully grown edge. New vertex is on the old boundary. Find new boundary on vertex
        elif:   Edge grown on itself. This cluster is already connected. Cut half-edge
        else:   Clusters merge by weighted union
        '''

        if passive_C is None:
            active_C.add_vertex(passive_V)
            passive_V.node = active_V.node
            self.cluster_new_vertex(active_C, passive_V, self.plot_growth)

        elif passive_C is active_C:
            edge.support -= 1
            if self.plot: self.plot.add_edge(edge, active_V)

        else:
            root_node = eg.adoption(active_V, passive_V, active_C, passive_C)
            if passive_C.size < active_C.size:
                active_C, passive_C = passive_C, active_C
            if self.print_steps:
                if active_C.cID not in self.mstr:
                    self.mstr[active_C.cID] = pr.print_graph(self.graph, [active_C], return_string=True)
                if passive_C.cID not in self.mstr:
                    self.mstr[passive_C.cID] = pr.print_graph(self.graph, [passive_C], return_string=True)
                self.mstr[passive_C.cID] += "\n" + self.mstr[active_C.cID]
                self.mstr.pop(active_C.cID)
            self.union_clusters(passive_C, active_C)
            passive_C.boundary[0].extend(active_C.boundary[0])
            passive_C.root_node = root_node


class planar(uf.planar, toric):

    '''
    ##################################################################################################

                                    0. Find clusters on boundary

    ##################################################################################################
    '''
    def find_clusters_boundary(self, *args, **kwargs):

        bound_clusters = []
        self.bound_cluster_vertices = []

        erasure_bound = []
        for layer in self.graph.B.values():
            for bound in layer.values():
                for vertex, edge in bound.neighbors.values():
                    if edge.qubit.erasure:
                        cluster = self.graph.get_cluster(self.graph.cID, bound)
                        cluster.on_bound = 1
                        bound_clusters.append(cluster)
                        self.bound_cluster_vertices.append([bound])
                        erasure_bound.append(bound)
                        bound.node = eg.boundary_node(bound)
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


    def cluster_new_vertex_boundary(self, bound_list, *args, **kwargs):

        if not bound_list:
            return

        new_list = []

        for vertex in bound_list:
            for (new_vertex, new_edge) in vertex.neighbors.values():

                if new_edge.qubit.erasure:
                    # if edge not already traversed
                    if new_edge.support == 0 and not new_edge.peeled:
                        if new_vertex.cluster is None:  # if no cycle detected
                            new_edge.support = 2
                            vertex.cluster.add_vertex(new_vertex)
                            eg.new_empty(vertex, new_vertex, vertex.cluster)
                            self.bound_cluster_edges[vertex.cluster.cID].append(new_edge)
                            self.bound_cluster_vertices[vertex.cluster.cID].append(new_vertex)
                            if self.plot and self.plot_find:
                                self.plot.plot_edge_step(new_edge, "confirm")
                            new_list.append(new_vertex)
                        else:  # cycle detected, peel edge
                            new_edge.peeled = True
                            if self.plot and self.plot_find:
                                self.plot.plot_edge_step(new_edge, "remove")
                else:
                    # Make sure new bound does not lead to self
                    if new_vertex.cluster is not vertex.cluster:
                        vertex.cluster.boundary[0].append((vertex, new_edge, new_vertex))

        self.cluster_new_vertex_boundary(new_list)
