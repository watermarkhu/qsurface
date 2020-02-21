'''
2020 Mark Shui Hu, QuTech

www.github.com/watermarkhu/toric_code
_____________________________________________

The Union-Find decoder as described by arXiv:1709.06218v1, altered to support evengrow

An OOP implementation has been made here, where the boundary and support are not stored as separate lists, which have to accesed based on some key value of the cluster. We store the boundary list and support for each cluster, and other paramters, directly at the cluster object.
The decoder requires a graph object, containing the vertices (stabilizers) and edges (qubits) of the uf-lattice. The graph can either be 2D (perfect measurements) or 2D (noisy measurements).
This impletementation has full integrated the evengrow algorithm, where boundary edges are not stored at the cluster, but rather at the basetree-nodes.
Two decoder classes are defined in this file, toric and planar for their respective lattice types.
'''

import unionfind as uf
import printing as pr


class toric(uf.toric):
    '''
    Union-Find evengrow-integrated decoder for the toric lattice (2D and 3D)
    Inherits all the class variables and methods of unionfind.toric

    Additions:
        eg      evengrow classes

    replaces:
        get_counts()                counts additionaly for evengrow hearistics
        cluster_new_vertex()        append boundary edges to vertices, base-tree empty-node initiation for erasure
        find_clusters()             base-tree anyon-node initiation, save boundary edges to vertices
        grow_bucket()               Save boundary edges from vertices to nodes
        grow_boundary_directed()    Grow boundary edges from node, for directed base-tree
        grow_boundary_undirected()  Grow boundary edges from node, for undirected base-tree
        fuse_vertices_degenerate()  Additionally sorts for base-tree node parities
        fully_grown_edge()          Adoption of base-trees, save root_node of cluster
        edge_growth_choices()       Copy cluster node to new vertices
    '''
    def __init__(self, *args, **kwargs):
        '''
        Optionally acceps config dict which contains plotting options.
        Counters for decoder specific heuristics are initialized.
        Decoder options, defined in kwargs are stored as class variables.
        '''
        super().__init__(*args, **kwargs)
        if self.directed_graph:
            self.grow_boundary = self.grow_boundary_directed
            import evengrow_directed as eg
        else:
            self.grow_boundary = self.grow_boundary_undirected
            import evengrow_undirected as eg
        self.eg = eg.eg()


    def get_counts(self):
        '''
        Appends counter values to list and resets them for new iteration
        Counts additionaly for evengrow hearistics
        '''
        super().get_counts()
        self.eg.get_counts()

    '''
    ##################################################################################################

                                        General helper funtions

    ##################################################################################################
    '''

    def cluster_new_vertex(self, cluster, vertex, plot_step=0, *args, **kwargs):
        """
        Recursive function which adds all connected erasure edges to a cluster, or finds the boundary on a vertex.

        For a given vertex, this function finds the neighboring edges and vertices that are in the the currunt cluster. Any new vertex or edge will be added to the graph.
        If the newly found edge is part of the erasure, the edge and the corresponding vertex will be added to the cluster, and the function is started again on the new vertex. Otherwise it will be added to the boundary.
        If a vertex is an anyon, its property and the parity of the cluster will be updated accordingly.
        Additionally appends boundary edges to vertices, base-tree empty-node
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
        Additionally initiates base-tree anyon-node, save boundary edges to vertices.
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

        if self.plot and not self.plot_find:
            self.plot.plot_removed("Clusters initiated")
            self.plot.draw_plot()
    '''
    ##################################################################################################

                                            2(a). Grow clusters expand

                                            top:    grow_clusters
                                            mid:    grow_bucket
                                            bot:    grow_boundary

    ##################################################################################################
    '''

    def grow_bucket(self, bucket, bucket_i, *args, **kwargs):
        '''
        Loops over all buckets to grow each bucket iteratively.
        Skips empty buckets during loop and breaks out when the largest bucket has been reached (defined by self.maxbucket)
        Additionally saves boundary edges from vertices to nodes.
        '''
        self.c_gbu += 1

        if self.print_steps:
            self.mstr = {}
            pr.printlog(
            "\n############################ GROW ############################" + f"\nGrowing bucket {bucket_i} of {self.maxbucket}: {bucket}" + f"\nRemaining buckets: {self.buckets[bucket_i + 1 : self.maxbucket + 1]}, {self.wastebucket}\n"
            )
        elif self.plot:
            print(f"Growing bucket #{bucket_i}/{self.maxbucket}")

        if self.plot and not self.plot_growth:
            self.plot.new_iter(f"Bucket {bucket_i} grown")


        self.fusion, self.bound_vertices, place = [], [], [] # Initiate Fusion list

        while bucket:  # Loop over all clusters in the current bucket\
            cluster = self.find_cluster_root(bucket.pop())

            if cluster.bucket == bucket_i and cluster.support == bucket_i % 2:
                place.append(cluster)
                cluster.support = 1 - cluster.support

                if self.plot and self.plot_growth and not self.plot_nodes: self.plot.new_iter("bucket {}: {} grown".format(cluster.bucket, cluster))

                self.grow_boundary(cluster, cluster.root_node)

                if self.plot and self.plot_growth and not self.plot_nodes:
                    self.plot.draw_plot()

        if self.plot and not self.plot_growth:
            self.plot.draw_plot()

        if not place:
            return

        if self.plot and not self.plot_growth:
            self.plot.new_iter(f"Bucket {bucket_i} fused")

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
            self.plot.draw_plot()


    def grow_boundary_directed(self, cluster, node, *args, **kwargs):
        '''
        Grows the boundary list that is stored at the current node using the directed base-tree.
        Fully grown edges are added to the fusion list.
        '''
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

            if self.plot and self.plot_nodes: self.plot.new_iter("bucket {}: {}-{} grown".format(cluster.bucket, cluster, node))

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
            if self.plot and self.plot_nodes: self.plot.draw_plot()
        else:
            node.w += 1

        for child in node.children:
            self.grow_boundary_directed(cluster, child)


    def grow_boundary_undirected(self, cluster, node, ancestor=None, *args, **kwargs):
        '''
        Grows the boundary list that is stored at the current node using the directed base-tree.
        Fully grown edges are added to the fusion list.
        '''
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
            if self.plot and self.plot_nodes: self.plot.new_iter("bucket {}: {}-{} grown".format(cluster.bucket, cluster, node))

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

            if self.plot and self.plot_nodes: self.plot.draw_plot()
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
        '''
        Fuse all edges in the fusion list by considering the vertex connectivity degeneracy.
        During a union of two clusters, there may be multiple edges in the fusion list that connect these clusters. We loop over all edges to count the number of fusion edges that is connected to the nodes involved. Fusion edges that are connected to vertices with high fusion edge connectivity equals a higher degeneracy in the number of edges to connect two clusters.
        We order the fusion edges by this vertex connectivity degeneracy and grows the largest degenerate edges first.
        Additionally sorts for base-tree node parities. A 0-0 union between base-tree nodes ensures low matching weight within the cluster, 0-1/1-0 is larger and wost is 1-1.
        '''
        merging = []
        for aV, edge, pV in self.fusion:
            aC = self.find_vertex_cluster(aV)
            pC = self.find_vertex_cluster(pV)

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
        '''
        Performs union of two clusters (belonging to aV and pV vertices) on a fully grown edge if its eligeable. Additionally applies adoption of base-trees, saves root_node of cluster.
        '''
        aC = self.find_vertex_cluster(aV)
        pC = self.find_vertex_cluster(pV)

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
        '''
        Checks the type of the fully grown edge.
        1. if:     Fully grown edge. New vertex is on the old boundary. Find new boundary on vertex
        2. elif:   Edge grown on itself. This cluster is already connected. Cut half-edge
        3. else:   Edge is between two separate clusters. Returns true to perform some function
        Additionally copies cluster node to new vertices.
        '''
        union = False
        if pC is None:
            aC.add_vertex(pV)
            pV.node = aV.node
            self.cluster_new_vertex(aC, pV, self.plot_growth)
            self.bound_vertices.append(pV)

        elif pC is aC:
            edge.support -= 1
            if self.plot:
                if self.plot_growth: self.plot.new_iter(str(edge) + " cut")
                self.plot.add_edge(edge, aV)
                if self.plot_growth: self.plot.draw_plot()
        else:
            union = True
        return union



class planar(uf.planar, toric):
    '''
    Union-Find evengrow-integrated decoder for the toric lattice (2D and 3D)
    Inherits all the class variables and methods of unionfind.planar and toric objects.
    Method resolution order:

    planar -> unionfind.planar -> toric -> unionfind.toric

    Initilized using the toric.__init__() function. And therefore has the addditions and replacements of the toric object, and additionally:

    replaces:
        find_clusters_boundary()        initiation of boundary nodes
        cluster_new_vertex_boundary()   initation of empty nodes
        edge_growth_choices()           check for second connection to boundary, copy cluster node to new vertices
    '''

    '''
    ##################################################################################################

                                    0. Find clusters on boundary

    ##################################################################################################
    '''
    def find_clusters_boundary(self, *args, **kwargs):
        '''
        For the planar lattice, in the case of erasures connected to the boundary, clusters need to be formed from the boundary, such that the shortest path from an anyon to the boundary is formed within the cluster tree.
        We loop over all edges connected to the boundary to find erasures and initate clusters from the boundary. If the cluster parity is larger than one, or if it actually contains an anyon, it is added to the lists of clusters. Otherwise, it is rememoved.
        Additionally initates boundary nodes on boundary vertices.
        '''
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

        if self.plot and not self.plot_find:
            self.plot.plot_removed("Boundary clusters initiated")
            self.plot.draw_plot()


    def cluster_new_vertex_boundary(self, bound_list, *args, **kwargs):
        '''
        Similar to cluster_new_vertex(), this function has the goal of doing a walk over the erasure edges to add all connected edges to the cluster, or to add the edge to the boundary if there is no erasure.
        Whereas cluster_new_vertex() runs recursively and therefore sequentially from each erasure, this functions runs iteratively over all erasures and walks a distance of 1 edge per iteration over all connected erasures.
        This ensures that any anyon has minimal distance to the boundary within the cluster tree.
        Additionally initiates empty nodes.
        '''
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
        '''
        Checks the type of the fully grown edge.
        1. if:      Edge grown on own cluster or second connection to the boundary. Cut half-edge
        2. elif:    Fully grown edge. New vertex is on the old boundary. Find new boundary on vertex
        3. else:    Edge is between two separate clusters. Returns true to perform some function
        Additionally copies cluster node to new vertices.
        '''
        union = False

        if (aC.on_bound and (pV.type == 1 or (pC is not None and pC.on_bound))) or pC is aC:
            edge.support -= 1
            if self.plot:
                if self.plot_growth: self.plot.new_iter(str(edge) + " cut")
                self.plot.add_edge(edge, aV)
                if self.plot_growth: self.plot.draw_plot()
        elif pC is None:
            aC.add_vertex(pV)
            pV.node = aV.node
            self.cluster_new_vertex(aC, pV, self.plot_growth)
            self.bound_vertices.append(pV)
        else:
            union = True
        return union
