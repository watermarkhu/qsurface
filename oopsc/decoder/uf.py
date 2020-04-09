'''
2020 Mark Shui Hu, QuTech

www.github.com/watermarkhu/oop_surface_code
_____________________________________________

The Union-Find decoder as described by arXiv:1709.06218v1

An OOP implementation has been made here, where the boundary and support are not stored as separate lists, which have to accesed based on some key value of the cluster. We store the boundary list and support for each cluster, and other paramters, directly at the cluster object.
The decoder requires a graph object, containing the vertices (stabilizers) and edges (qubits) of the uf-lattice. The graph can either be 2D (perfect measurements) or 2D (noisy measurements).
Two decoder classes are defined in this file, toric and planar for their respective lattice types.
'''


from ..info.decorators import debug, plot
from ..info import printing as pr


class toric(object):
    '''
    Union-Find decoder for the toric lattice (2D and 3D)
    '''
    @debug.init_counters_uf()
    def __init__(self, plot_config=None, *args, **kwargs):
        '''
        Optionally acceps config dict which contains plotting options.
        Counters for decoder specific heuristics are initialized.
        Decoder options, defined in kwargs are stored as class variables.
        '''
        self.type = "uf"
        self.plot_config = plot_config

        for key, value in kwargs.items():
            setattr(self, key, value)

        self.plot_growth = not (self.plot_bucket or self.plot_cluster)

        if self.dg_connections:
            self.fuse_vertices = self.fuse_vertices_degenerate
        else:
            self.fuse_vertices = self.fuse_vertices_simple


    @debug.get_counters()
    def decode(self, *args, **kwargs):
        '''
        Decode functions for the Union-Find toric decoder
        '''
        self.plot = self.graph.init_uf_plot() if self.graph.plotUF else None
        self.init_buckets()
        self.find_clusters()
        self.grow_clusters()
        self.peel_clusters()

    '''
    ##################################################################################################

                                            UNION-FIND funtions

    ##################################################################################################
    '''

    @debug.counter(name="ufu")
    def union_clusters(self, parent, child, *args, **kwargs):
        """
        Merges two clusters by updating the parent/child relationship and updating the attributes
        Union of UF algorithm
        """
        child.parent = parent
        parent.size += child.size
        parent.parity += child.parity

    @debug.counter(name="uff")
    def find(self, cluster):
        '''
        Find parent of cluster. Applies path compression.
        Find of UF algorithm.
        '''
        if cluster is not cluster.parent:
            cluster.parent = self.find(cluster.parent)
        return cluster.parent


    def get_cluster_root(self, cluster, *args, **kwargs):
        """
        Loops through the cluster tree to find the root cluster of the given cluster. When the parent cluster is not at the root level, the function is started again on the parent cluster. The recursiveness of the function makes sure that at each level the parent is pointed towards the root cluster, furfilling the collapsing rule.
        """

        if cluster is not None:
            if cluster.parent is not cluster.parent.parent:
                self.find(cluster)
            return cluster.parent
        else:
            return None


    def get_vertex_cluster(self, vertex):
        '''
        Returns the cluster to which the input vertex belongs to.
        '''
        cluster = self.get_cluster_root(vertex.cluster)

        if cluster is None:
            return None
        else:
            vertex.cluster = cluster.parent
            return cluster.parent


    '''
    ##################################################################################################

                                        General helper funtions

    ##################################################################################################
    '''

    def cluster_place_bucket(self, cluster, *args, **kwargs):
        """
        :param cluster      current cluster

        The inputted cluster has undergone a size change, either due to cluster growth or during a cluster merge, in which case the new root cluster is inputted. We increase the appropiate bucket number of the cluster intil the fitting bucket has been reached. The cluster is then appended to that bucket.
        If the max bucket number has been reached. The cluster is appended to the wastebucket, which will never be selected for growth.
            """

        cluster.bucket = 2 * (cluster.size - 1) + cluster.support

        if (cluster.parity % 2 == 1 and not cluster.on_bound) and cluster.bucket < self.numbuckets:
            self.buckets[cluster.bucket].append(cluster)
            if cluster.bucket > self.maxbucket:
                self.maxbucket = cluster.bucket
        else:
            cluster.bucket = None


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
                        if self.plot and plot_step:
                            self.plot.plot_edge_step(new_edge, "confirm")
                        self.cluster_new_vertex(cluster, new_vertex, plot_step)
                    else:  # cycle detected, peel edge
                        new_edge.peeled = True
                        print(new_edge)
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
    def init_buckets(self):
        '''
        initializes buckets for bucket growth
        '''
        self.numbuckets = self.graph.size**(self.graph.dim)   #* (self.graph.size//2)**(self.graph.dim-1) * 2
        self.buckets = [[] for _ in range(self.numbuckets)]
        self.wastebucket = []
        self.maxbucket = 0


    @plot.iter(name="Clusters found", cname="plot_find", dname="plot_removed")
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

        for vertex in anyons:
            if vertex.cluster is None:
                cluster = self.graph.add_cluster(self.graph.cID, vertex)
                self.cluster_new_vertex(cluster, vertex, self.plot_find)
                self.cluster_place_bucket(cluster)
                self.graph.cID += 1

    '''
    ##################################################################################################

                                            2(a). Grow clusters expand

                                            top:    grow_clusters
                                            mid:    grow_bucket
                                            bot:    grow_boundary

    ##################################################################################################
    '''
    @plot.iter(name="Clusters grown", cname="plot_growth", flip=False)
    def grow_clusters(self, start_bucket=0, *args, **kwargs):
        '''
        Loops over all buckets to grow each bucket iteratively.
        Skips empty buckets during loop and breaks out when the largest bucket has been reached (defined by self.maxbucket)
        '''

        if self.print_steps:
            pr.print_graph(self.graph)

        for bucket_i, bucket in enumerate(self.buckets[start_bucket:], start_bucket):

            if bucket_i > self.maxbucket:
                break

            if not bucket:  # no need to check empty bucket
                continue

            self.grow_bucket(bucket, bucket_i)
            if self.place:
                self.fuse_bucket(bucket_i)

            if self.print_steps:
                pr.print_graph(self.graph, printmerged=0)


    @debug.counter(name="gbu")
    @plot.iter_grow_bucket()
    def grow_bucket(self, bucket, bucket_i, *args, **kwargs):
        '''
        Grows the clusters which are contained in the current bucket.
        Skips the cluster if it is already contained in a higher bucket or if the support parameters does not equal the current bucket support
        '''
        self.fusion, self.place = [], []  # Initiate Fusion list
        while bucket:  # Loop over all clusters in the current bucket\
            cluster = self.get_cluster_root(bucket.pop())
            if cluster.bucket == bucket_i and cluster.support == bucket_i % 2:
                self.place.append(cluster)
                cluster.support = 1 - cluster.support
                self.grow_boundary(cluster, bucket_i)


    @debug.counter(name="gbo")
    @plot.iter_grow_boundary()
    def grow_boundary(self, cluster, *args, **kwargs):
        '''
        Grows the boundary list that is stored at the current cluster.
        Fully grown edges are added to the fusion list.
        '''
        cluster.boundary = [[], cluster.boundary[0]]     # Set boudary

        while cluster.boundary[1]:                       # grow boundary
            bound = cluster.boundary[1].pop()
            vertex, new_edge, new_vertex = bound

            if new_edge.support != 2:                    # if not already fully grown
                new_edge.support += 1                    # Grow boundaries by half-edge
                if new_edge.support == 2:                # if edge is fully grown
                    self.fusion.append(bound)            # Append to fusion list of edges
                else:
                    cluster.boundary[0].append(bound)
                if self.plot: self.plot.add_edge(new_edge, vertex)


    @plot.iter_fuse_bucket()
    def fuse_bucket(self, bucket_i, *args, **kwrags):
        '''
        Put clusters in new buckets. Some will be added double, but will be skipped by the new_boundary check
        '''
        self.fuse_vertices()
        for cluster in self.place:
            cluster = self.get_cluster_root(cluster)
            self.cluster_place_bucket(cluster)



    '''
    ##################################################################################################

                                            2(b). Grow clusters fuse

    ##################################################################################################
    '''


    def fuse_vertices_simple(self, *args, **kwargs):
        '''
        Fuse all edges in the fusion list by edge order in the list.
        '''
        for aV, edge, pV in self.fusion:
            self.fully_grown_edge(edge, aV, pV)


    def fuse_vertices_degenerate(self, *args, **kwargs):
        '''
        Fuse all edges in the fusion list by considering the vertex connectivity degeneracy.
        During a union of two clusters, there may be multiple edges in the fusion list that connect these clusters. We loop over all edges to count the number of fusion edges that is connected to the nodes involved. Fusion edges that are connected to vertices with high fusion edge connectivity equals a higher degeneracy in the number of edges to connect two clusters.
        We order the fusion edges by this vertex connectivity degeneracy and grows the largest degenerate edges first.
        '''

        merging = []
        for aV, edge, pV in self.fusion:
            aC = self.get_vertex_cluster(aV)
            pC = self.get_vertex_cluster(pV)

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

        merge_buckets = [[] for i in range(6)]
        for mergevertices in merging:
            edge, aV, pV = mergevertices
            index = 7 - (aV.count + pV.count)
            merge_buckets[index].append(mergevertices)

        for merge_bucket in merge_buckets:
            for items in merge_bucket:
                self.fully_grown_edge(*items)


    def fully_grown_edge(self, edge, aV, pV, *args, **kwargs):
        '''
        Performs union of two clusters (belonging to aV and pV vertices) on a fully grown edge if its eligeable.
        '''
        aC = self.get_vertex_cluster(aV)
        pC = self.get_vertex_cluster(pV)

        if self.edge_growth_choices(edge, aV, pV, aC, pC):
            if pC.size < aC.size:  # of clusters
                aC, pC = pC, aC
            if self.print_steps:                            # Keep track of which clusters are merged into one to print later
                if aC.cID not in self.mstr:
                    self.mstr[aC.cID] = pr.print_graph(self.graph, [aC], return_string=True)
                if pC.cID not in self.mstr:
                    self.mstr[pC.cID] = pr.print_graph(self.graph, [pC], return_string=True)
                self.mstr[pC.cID] += "\n" + self.mstr[aC.cID]
                self.mstr.pop(aC.cID)
            self.union_clusters(pC, aC)
            pC.boundary[0].extend(aC.boundary[0])                      # Combine boundaries


    def edge_growth_choices(self, edge, aV, pV, aC, pC):
        '''
        Checks the type of the fully grown edge.
        1. if:     Fully grown edge. New vertex is on the old boundary. Find new boundary on vertex
        2. elif:   Edge grown on itself. This cluster is already connected. Cut half-edge
        3. else:   Edge is between two separate clusters. Returns true to perform some function
        '''
        union = False
        if pC is None:
            aC.add_vertex(pV)
            self.cluster_new_vertex(aC, pV, self.plot_growth)
        elif pC is aC:
            edge.support = 0
            if self.plot:
                if self.plot_cut: self.plot.new_iter(str(edge) + " cut")
                self.plot.add_edge(edge, aV)
                if self.plot_cut: self.plot.draw_plot()
        else:
            union = True
        return union


    '''
    ##################################################################################################

                                            3. Peel clusters

    ##################################################################################################
    '''
    @plot.iter_peel_clusters()
    def peel_clusters(self, *args, **kwargs):
        """
        Loops overal all vertices to find pendant vertices which are selected from peeling using {peel_edge}

        """
        for layer in self.graph.S.values():
            for vertex in layer.values():
                if vertex.cluster is not None:
                    cluster = self.get_vertex_cluster(vertex)
                    self.peel_edge(cluster, vertex)


    def peel_edge(self, cluster, vertex, *args, **kwargs):
        """
        :param cluster          current active cluster
        :param vertex           pendant vertex of the edge to be peeled

        Recursive function which peels a branch of the tree if the input vertex is a pendant vertex

        If there is only one neighbor of the input vertex that is in the same cluster, this vertex is a pendant vertex and can be peeled. The function calls itself on the other vertex of the edge leaf.
        """
        plot = True if self.plot and self.plot_peel else False
        num_connect = 0

        for (NV, NE) in vertex.neighbors.values():
            if NE.support == 2 and not NE.peeled:
                new_cluster = self.get_vertex_cluster(NV)
                if new_cluster is cluster:
                    num_connect += 1
                    edge, new_vertex = NE, NV
                if num_connect > 1:
                    break

        if num_connect == 1:
            edge.peeled = True
            if vertex.state:

                if edge.edge_type == 0:
                    decode_edge = self.graph.Q[self.graph.decode_layer][edge.qubit.qID].E[edge.ertype]
                    decode_edge.state = not decode_edge.state

                edge.matching = True
                vertex.state = False
                new_vertex.state = not new_vertex.state

                if plot:
                    self.plot.plot_edge_step(edge, "match")
                    self.plot.plot_strip_step_anyon(vertex)
                    if new_vertex.type == 0:
                        self.plot.plot_strip_step_anyon(new_vertex)
            else:
                if plot:
                    self.plot.plot_edge_step(edge, "peel")
            self.peel_edge(cluster, new_vertex)


class planar(toric):
    '''
    Union-Find decoder for the planar lattice (2D and 3D)
    Inherits all the class variables and methods of toric

    replaces:
        decode()                        find clusters on boundary first
        union_clusters()                copy on_bound paramter to parent cluster
        cluster_new_vertex()            check if new vertex is a boundary and save to cluster
        edge_growth_choices()           check if cluster already has a connection to the boundary

    additions:
        find_clusters_boundary()        find cluster from the boundary to ensure minimal path within cluster tree
        cluster_new_vertex_boundary()   walk over erasures iteratively to find all edges in the cluster
    '''
    @debug.get_counters()
    def decode(self, *args, **kwargs):
        '''
        Decode functions for the Union-Find planar decoder
        '''
        self.plot = self.graph.init_uf_plot() if self.graph.plotUF else None
        self.init_buckets()
        self.find_clusters_boundary()
        self.find_clusters()
        self.grow_clusters()
        self.peel_clusters()

    '''s
    ##################################################################################################

                                            UNION-FIND funtions

    ##################################################################################################
    '''
    def union_clusters(self, parent, child, *args, **kwargs):
        """
        Merges two clusters by updating the parent/child relationship and updating the attributes
        """
        super().union_clusters(parent, child, *args, **kwargs)
        parent.on_bound = parent.on_bound or child.on_bound

    '''
    ##################################################################################################

                                        General helper funtions

    ##################################################################################################
    '''

    def cluster_new_vertex(self, cluster, vertex, plot_step=0, *args, **kwargs):
        '''
        :param cluster          current cluster
        :param vertex           vertex that is recently added to the cluster

        Recursive function which adds all connected erasure edges to a cluster, or finds the boundary on a vertex.

        For a given vertex, this function finds the neighboring edges and vertices that are in the the currunt cluster. Any new vertex or edge will be added to the graph.
        If the newly found edge is part of the erasure, the edge and the corresponding vertex will be added to the cluster, and the function is started again on the new vertex. Otherwise it will be added to the boundary.
        If a vertex is an anyon, its property and the parity of the cluster will be updated accordingly.
        '''

        if vertex.type == 1:
            cluster.on_bound = 1

        super().cluster_new_vertex(cluster, vertex, plot_step, *args, **kwargs)

    '''
    ##################################################################################################

                                    0. Find clusters on boundary

    ##################################################################################################
    '''
    @plot.iter(name="Boundary clusters found", cname="plot_find", dname="plot_removed")
    def find_clusters_boundary(self, *args, **kwargs):
        '''
        For the planar lattice, in the case of erasures connected to the boundary, clusters need to be formed from the boundary, such that the shortest path from an anyon to the boundary is formed within the cluster tree.
        We loop over all edges connected to the boundary to find erasures and initate clusters from the boundary. If the cluster parity is larger than one, or if it actually contains an anyon, it is added to the lists of clusters. Otherwise, it is rememoved.
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
                        self.graph.cID += 1

        # Walk over erasure edges to get entire cluster
        self.bound_cluster_edges = [[] for _ in range(self.graph.cID)]
        self.cluster_new_vertex_boundary(erasure_bound)

        # Check parity of clusters. Save if parity is larger than 1.
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
        '''
        Similar to cluster_new_vertex(), this function has the goal of doing a walk over the erasure edges to add all connected edges to the cluster, or to add the edge to the boundary if there is no erasure.
        Whereas cluster_new_vertex() runs recursively and therefore sequentially from each erasure, this functions runs iteratively over all erasures and walks a distance of 1 edge per iteration over all connected erasures.
        This ensures that any anyon has minimal distance to the boundary within the cluster tree.
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
        '''
        union = False

        if (aC.on_bound and (pV.type == 1 or (pC is not None and pC.on_bound))) or pC is aC:
            edge.support = 0
            if self.plot:
                if self.plot_cut: self.plot.new_iter(str(edge) + " cut")
                self.plot.add_edge(edge, aV)
                if self.plot_cut: self.plot.draw_plot()
        elif pC is None:
            aC.add_vertex(pV)
            self.cluster_new_vertex(aC, pV, self.plot_growth)
        else:
            union = True
        return union
