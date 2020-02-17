'''
2020 Mark Shui Hu, QuTech

www.github.com/watermarkhu/toric_code
_____________________________________________
'''

import unionfind as uf
import printing as pr


class toric(uf.toric):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.directed_graph:
            self.grow_boundary = self.grow_boundary_directed
            import evengrow_directed as eg
        else:
            self.grow_boundary = self.grow_boundary_undirected
            import evengrow_undirected as eg
        self.eg = eg.eg()


    def get_counts(self):
        super().get_counts()
        self.eg.get_counts()

    '''
    ##################################################################################################

                                        General helper funtions

    ##################################################################################################
    '''

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
                if new_edge.support == 0 and not new_edge.peeled:
                    # if edge not already traversed
                    if new_vertex.cluster is None:  # if no cycle detected
                        new_edge.support = 2
                        cluster.add_vertex(new_vertex)
                        self.eg.new_empty(vertex, new_vertex, cluster)

                        if self.plot and plot_step:
                            self.plot.plot_edge_step(new_edge, "confirm")
                        self.cluster_new_vertex(cluster, vertex, plot_step)
                    else:  # cycle detected, peel edge
                        new_edge.peeled = True
                        if self.plot and plot_step:
                            self.plot.plot_edge_step(new_edge, "remove")
            else:
                # Make sure new bound does not lead to self
                if new_vertex.cluster is not cluster:
                    vertex.new_bound.append((vertex, new_edge, new_vertex))

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
                    vertex.node = self.eg.anyon_node(vertex)

        for vertex in anyons:
            if vertex.cluster is None:
                cluster = self.graph.add_cluster(self.graph.cID, vertex)
                self.cluster_new_vertex(cluster, vertex, self.plot_find)
                vertex.node.boundary[0], vertex.new_bound = vertex.new_bound, []
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

    def grow_bucket(self, bucket, bucket_i, *args, **kwargs):

        self.c_gbu += 1

        if self.print_steps: self.mstr = {}
        self.fusion, self.bound_vertices, place = [], [], [] # Initiate Fusion list

        while bucket:  # Loop over all clusters in the current bucket\
            cluster = self.find_cluster_root(bucket.pop())

            if cluster.bucket == bucket_i and cluster.support == bucket_i % 2:
                place.append(cluster)
                cluster.support = 1 - cluster.support
                self.grow_boundary(cluster, cluster.root_node)

                if self.plot_growth: self.plot.draw_plot(str(cluster) + " grown.")

        self.fuse_vertices()

        # Save new boundaries from vertices to nodes
        for vertex in self.bound_vertices:
            while vertex.new_bound:
                vertex.node.boundary[0].append(vertex.new_bound.pop())

        # Put clusters in new buckets. Some will be added double, but will be skipped by the new_boundary check
        for cluster in place:
            cluster = self.find_cluster_root(cluster)
            self.cluster_place_bucket(cluster)

        if self.print_steps:
            pr.printlog("")
            for cID, string in self.mstr.items():
                pr.printlog(f"B:\n{string}\nA:\n{pr.print_graph(self.graph, [self.graph.C[cID]], include_even=1, return_string=True)}\n")

        if self.plot and not self.plot_growth:
            self.plot.draw_plot("Clusters merged")


    def grow_boundary_directed(self, cluster, node, *args, **kwargs):

        self.c_gbo += 1

        if cluster.root_node.calc_delay and self.print_steps:
            if type(cluster.root_node.calc_delay) == list:
                calc_nodes = [node.short_id() for node, edge, ancestor in cluster.root_node.calc_delay]
                print_tree = False
            else:
                calc_nodes = [node.short_id() for node in cluster.root_node.calc_delay]
                print_tree = True
            print("Computing delay root {} at nodes {} and children".format(cluster.root_node.short_id(), calc_nodes))

        else:
            print_tree = False

        while cluster.root_node.calc_delay:

            at_node = cluster.root_node.calc_delay.pop()
            self.eg.comp_tree_p_of_node(at_node)
            self.eg.comp_tree_d_of_node(at_node, cluster)


        if print_tree:
            pr.print_tree(cluster.root_node, "children", "tree_rep")

        if node.d - node.w == cluster.mindl:      # waited enough rounds as delay
            node.s += 1

            node.boundary = [[], node.boundary[0]]
            while node.boundary[1]:

                bound = node.boundary[1].pop()
                vertex, new_edge, new_vertex = bound

                if new_edge.support != 2:

                    new_edge.support += 1

                    if new_edge.support == 2:                   # if edge is fully grown
                        self.fusion.append(bound)               # Append to fusion list
                    else:
                        node.boundary[0].append(bound)

                    if self.plot: self.plot.add_edge(new_edge, vertex)

            if self.plot and self.plot_nodes: self.plot.draw_plot(str(node) + " grown.")
        else:
            node.w += 1

        for child in node.children:
            self.grow_boundary_directed(cluster, child)


    def grow_boundary_undirected(self, cluster, node, ancestor=None, *args, **kwargs):

        self.c_gbo += 1

        if cluster.root_node.calc_delay and self.print_steps:
            if type(cluster.root_node.calc_delay) == list:
                calc_nodes = [node.short_id() for node, edge, ancestor in cluster.root_node.calc_delay]
                print_tree = False
            else:
                calc_nodes = [node.short_id() for node in cluster.root_node.calc_delay]
                print_tree = True
            print("Computing delay root {} at nodes {} and children".format(cluster.root_node.short_id(), calc_nodes))

        else:
            print_tree = False

        while cluster.root_node.calc_delay:
            at_node, at_edge, at_ancestor = cluster.root_node.calc_delay.pop()
            self.eg.comp_tree_p_of_node(at_node, at_ancestor)
            self.eg.comp_tree_d_of_node(cluster, at_node, [at_ancestor, at_edge])

        if print_tree:
            pr.print_tree(cluster.root_node, "children", "tree_rep")

        if node.d - node.w == cluster.mindl:      # waited enough rounds as delay
            node.s += 1

            node.boundary = [[], node.boundary[0]]
            while node.boundary[1]:

                bound = node.boundary[1].pop()
                vertex, new_edge, new_vertex = bound

                if new_edge.support != 2:

                    new_edge.support += 1

                    if new_edge.support == 2:                   # if edge is fully grown
                        self.fusion.append(bound)               # Append to fusion list
                    else:
                        node.boundary[0].append(bound)

                    if self.plot: self.plot.add_edge(new_edge, vertex)

            if self.plot and self.plot_nodes: self.plot.draw_plot(str(node) + " grown.")
        else:
            node.w += 1

        for child, _ in node.cons:
            if child is not ancestor:
                self.grow_boundary_undirected(cluster, child, ancestor=node)


    '''
    ##################################################################################################

                                            2(b). Grow clusters fuse

    ##################################################################################################
    '''

    def fuse_vertices_degenerate(self, *args, **kwargs):


        merging = []
        for aV, edge, pV in self.fusion:
            aC = self.find_vertex_cluster(aV)
            pC = self.find_vertex_cluster(pV)

            '''
            if:     Fully grown edge. New vertex is on the old boundary. Find new boundary on vertex
            elif:   Edge grown on itself. This cluster is already connected. Cut half-edge
            else:   Clusters merge by weighted union
            '''
            if self.edge_growth_choices(edge, aV, pV, aC, pC):
                aV.count, pV.count = 0, 0
                merging.append((edge, aV, pV))

        for edge, aV, pV in merging:
            aV.count += 1
            pV.count += 1

        merge_buckets = [[[] for _ in range(6)] for _ in range(3)]
        for mergevertices in merging:
            (edge, aV, pV) = mergevertices
            V_index = 7 - (aV.count + pV.count)

            if aV.node.p == 0 and pV.node.p == 0:
                A_index = 0
            elif aV.node.p == 0 or pV.node.p == 0:
                A_index = 1
            else:
                A_index = 2

            merge_buckets[A_index][V_index].append(mergevertices)

        for A_bucket in merge_buckets:
            for V_bucket in A_bucket:
                for items in V_bucket:
                    self.fully_grown_edge(*items)


    def fully_grown_edge(self, edge, aV, pV, *args, **kwargs):

        aC = self.find_vertex_cluster(aV)
        pC = self.find_vertex_cluster(pV)

        '''
        if:     Fully grown edge. New vertex is on the old boundary. Find new boundary on vertex
        elif:   Edge grown on itself. This cluster is already connected. Cut half-edge
        else:   Clusters merge by weighted union
        '''

        if self.edge_growth_choices(edge, aV, pV, aC, pC):
            root_node = self.eg.adoption(aV, pV, aC, pC)
            if pC.size < aC.size:
                aC, pC = pC, aC
            if self.print_steps:
                if aC.cID not in self.mstr:
                    self.mstr[aC.cID] = pr.print_graph(self.graph, [aC], return_string=True)
                if pC.cID not in self.mstr:
                    self.mstr[pC.cID] = pr.print_graph(self.graph, [pC], return_string=True)
                self.mstr[pC.cID] += "\n" + self.mstr[aC.cID]
                self.mstr.pop(aC.cID)
            self.union_clusters(pC, aC)
            pC.root_node = root_node


    def edge_growth_choices(self, edge, aV, pV, aC, pC):

        union = False
        if pC is None:
            aC.add_vertex(pV)
            pV.node = aV.node
            self.cluster_new_vertex(aC, pV, self.plot_growth)
            self.bound_vertices.append(pV)

        elif pC is aC:
            edge.support -= 1
            if self.plot: self.plot.add_edge(edge, aV)
        else:
            union = True
        return union



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
                        bound.node = self.eg.boundary_node(bound)
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
                            self.eg.new_empty(vertex, new_vertex, vertex.cluster)
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

    '''
    ##################################################################################################

                                            2(b). Grow clusters fuse

    ##################################################################################################
    '''
    def edge_growth_choices(self, edge, aV, pV, aC, pC):

        union = False

        if (aC.on_bound and (pV.type == 1 or (pC is not None and pC.on_bound))) or pC is aC:
            edge.support -= 1
            if self.plot: self.plot.add_edge(edge, aV)
        elif pC is None:
            aC.add_vertex(pV)
            pV.node = aV.node
            self.cluster_new_vertex(aC, pV, self.plot_growth)
            self.bound_vertices.append(pV)
        else:
            union = True
        return union
