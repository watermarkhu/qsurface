from ...codes.elements import AncillaQubit, PseudoQubit
from .._template import SimCode
from collections import defaultdict


class Cluster(object):
    """
    Cluster object with parameters:
    index         ID number of cluster
    size        size of this cluster based on the number contained vertices
    parity      parity of this cluster based on the number of contained anyons
    parent      the parent cluster of this cluster
    boundary    len(2) list containing 1) current boundary, 2) next boundary
    bucket      the appropiate bucket number of this cluster
    support     growth state of the cluster: 1 if False, 2 if True

    [planar]
    on_bound    whether this clusters is connected to the boundary

    """
    def __init__(self, index, instance, **kwargs):
        self.index      = index
        self.instance   = instance
        self.size       = 0
        self.parity     = 0
        self.parent     = self
        self.bound      = []
        self.new_bound  = []
        self.bucket     = -1
        self.support    = 0
        self.on_bound   = 0

    def __repr__(self):
        sep = "|" if self.on_bound else ":"
        return "C{}({}{}{})".format(self.index, self.size, sep, self.parity)

    def __hash__(self):
        return self.index, self.instance

    def add_vertex(self, vertex):
        """Adds a stabilizer to a cluster. Also update cluster value of this stabilizer."""
        vertex.cluster = self
        if type(vertex) is AncillaQubit:
            self.size += 1
            if vertex.measured_state:
                self.parity += 1
        elif type(vertex) is PseudoQubit:
            self.on_bound = True

    def union(self, cluster, **kwargs):
        """
        Merges two clusters by updating the parent/child relationship and updating the attributes
        Union of UF algorithm
        """
        if self.size < cluster.size:
            self, cluster = cluster, self
        cluster.parent = self
        self.size += cluster.size
        self.parity += cluster.parity
        self.new_bound.extend(cluster.new_bound)
        self.on_bound = self.on_bound or cluster.on_bound
        return self

    def find(self, **kwargs):
        '''
        Find parent of cluster. Applies path compression.
        Find of UF algorithm.
        '''
        if self.parent is not self:
            self.parent = self.parent.find()
        return self.parent


class Toric(SimCode):
    """Union-Find decoder for the toric lattice."""

    name = "Union-Find"
    short = "unionfind"

    compatibility_measurements = dict(
        PerfectMeasurements=True,
        FaultyMeasurements=False,
    )
    compatibility_errors = dict(
        pauli=True,
        erasure=False,
    )

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.config["step_growth"] = not (self.config["step_bucket"] or self.config["step_cluster"])
        self.code.ancillaQubit.cluster = None
        self.code.edge.peeled = None
        if not self.config["dynamic_forest"]:
            self.code.ancillaQubit.forest = None
            self.code.edge.forest = None

        self.support = {}
        for layer in self.code.data_qubits.values():
            for data_qubit in layer.values():
                for edge in data_qubit.edges.values():
                    self.support[edge] = 0
        if hasattr(self.code, "pseudo_edges"):
            for edge in self.code.pseudo_edges:
                self.support[edge] = 0

        if self.config["weighted_growth"]:
            self.buckets_num = self.code.size[0]*self.code.size[1]*self.code.layers*2
        else:
            self.buckets_num = 2

        self.buckets = defaultdict(list)
        self.init_reset()

    def init_reset(self):
        self.bucket_max_filled = 0
        self.cluster_index = 0
        self.clusters = []
        self.support = {edge: 0 for edge in self.support}


    def do_decode(self, reset=True, **kwargs):
        # Inherited docstrings
        self.find_clusters(**kwargs)
        self.grow_clusters(**kwargs)                          
        self.peel_clusters(**kwargs)

        if reset:
            self.init_reset()

    """
    ================================================================================================
                                    1. Find clusters
    ================================================================================================
    """

    def find_clusters(self, **kwargs):
        """
        Given a set of erased qubits/edges on a lattice, this functions finds all edges that are connected and sorts them in separate clusters. A single anyon can also be its own cluster.
        It loops over all vertices (randomly if toggled, which produces a different tree), and calls {cluster_new_vertex} to find all connected erasure qubits, and finds the boundary for growth step 1. Afterwards the cluster is placed in a bucket based in its size.

        """
        plaqs, stars = self.get_syndrome()

        for vertex in plaqs + stars:
            if vertex.cluster is None or vertex.cluster.instance != self.code.instance:
                cluster = Cluster(self.cluster_index, self.code.instance)
                cluster.add_vertex(vertex)
                self._cluster_find_vertices(cluster, vertex)
                self._cluster_place_bucket(cluster, -1)
                self.cluster_index += 1
                self.clusters.append(cluster)

        if self.config["print_steps"]:
            print(f"Found clusters:\n" + ", ".join(map(str, self.clusters)) +"\n")


    """
    ================================================================================================
                                    2(a). Grow clusters expansion
    ================================================================================================
    """
    def grow_clusters(self, start_bucket=0, **kwargs):
        '''
        Loops over all buckets to grow each bucket iteratively.
        Skips empty buckets during loop and breaks out when the largest bucket has been reached (defined by self.maxbucket)
        '''
        if self.config["weighted_growth"]:
            for bucket_i in range(start_bucket, self.buckets_num):
                if bucket_i > self.bucket_max_filled:
                    break
                if bucket_i in self.buckets and self.buckets[bucket_i] != []:
                    union_list, place_list = self._grow_bucket(self.buckets.pop(bucket_i), bucket_i)
                    self._fuse_bucket(union_list)
                    self._place_bucket(place_list, bucket_i)
        else:
            bucket_i = 0
            while self.buckets[0]:
                union_list, place_list = self._grow_bucket(self.buckets.pop(0), bucket_i)
                self._fuse_bucket(union_list)
                self._place_bucket(place_list, bucket_i)
                bucket_i += 1

    def _grow_bucket(self, bucket, bucket_i, **kwargs):
        '''
        Grows the clusters which are contained in the current bucket.
        Skips the cluster if it is already contained in a higher bucket or if the support parameters does not equal the current bucket support
        '''
        if self.config["print_steps"]:
            string = f"Growing bucket {bucket_i} of clusters:"
            print("="*len(string) + "\n" + string)

        union_list, place_list = [], [] 
        while bucket:  # Loop over all clusters in the current bucket\
            cluster = bucket.pop().find()
            if cluster.bucket == bucket_i and cluster.support == bucket_i % 2:
                place_list.append(cluster)
                self._grow_boundary(cluster, union_list)
        
        if self.config["print_steps"]:
            print("\n")
        
        return union_list, place_list

    def _grow_boundary(self, cluster, union_list, **kwargs):
        '''
        Grows the boundary list that is stored at the current cluster.
        Fully grown edges are added to the union_list list.
        '''
        cluster.support = 1 - cluster.support
        cluster.bound, cluster.new_bound = cluster.new_bound, []

        while cluster.bound:                       # grow boundary
            boundary = cluster.bound.pop()
            new_edge = boundary[1]

            if self.support[new_edge] != 2:              # if not already fully grown
                self.support[new_edge] += 1              # Grow boundaries by half-edge
                if self.support[new_edge] == 2:          # if edge is fully grown
                    union_list.append(boundary)            # Append to union_list list of edges
                else:
                    cluster.new_bound.append(boundary)

        if self.config["print_steps"]:
            print(f"{cluster}, ", end="")

    """
    ================================================================================================
                                    2(b). Grow clusters union
    ================================================================================================
    """
    def _fuse_bucket(self, union_list, **kwargs):
        '''
        Put clusters in new buckets. Some will be added double, but will be skipped by the new_boundary check.

        Fuse all edges in the union_list list by considering the vertex connectivity degeneracy.
        During a union of two clusters, there may be multiple edges in the union_list list that connect these clusters. We loop over all edges to count the number of union_list edges that is connected to the nodes involved. union_list edges that are connected to vertices with high union_list edge connectivity equals a higher degeneracy in the number of edges to connect two clusters.
        We order the union_list edges by this vertex connectivity degeneracy and grows the largest degenerate edges first.
        '''
        if union_list and self.config["print_steps"]:
            print("Fusing clusters")

        if self.config["degenerate_union"]:
            merging = []
            for vertex, edge, new_vertex in union_list:
                cluster = self._get_vertex_cluster(vertex)
                new_cluster = self._get_vertex_cluster(new_vertex)

                '''
                if:     Fully grown edge. New vertex is on the old boundary. Find new boundary on vertex
                elif:   Edge grown on itself. This cluster is already connected. Cut half-edge
                else:   Clusters merge by weighted union
                '''
                if self._edge_union_options(edge, new_vertex, cluster, new_cluster):
                    vertex.count, new_vertex.count = 0, 0
                    merging.append((edge, vertex, new_vertex))

            for edge, vertex, new_vertex in merging:
                vertex.count += 1
                new_vertex.count += 1

            merge_buckets = [[] for i in range(6)]
            for mergevertices in merging:
                edge, vertex, new_vertex = mergevertices
                index = 7 - (vertex.count + new_vertex.count)
                merge_buckets[index].append(mergevertices)

            for merge_bucket in merge_buckets:
                for items in merge_bucket:
                    self._fully_grown_edge(*items)
        else:
            for vertex, edge, new_vertex in union_list:
                self._fully_grown_edge(edge, vertex, new_vertex)

        if union_list and self.config["print_steps"]:
            print("")


    def _fully_grown_edge(self, edge, vertex, new_vertex, *args, **kwargs):
        '''
        Performs union of two clusters (belonging to vertex and new_vertex vertices) on a fully grown edge if its eligible.
        '''
        cluster = self._get_vertex_cluster(vertex)
        new_cluster = self._get_vertex_cluster(new_vertex)

        if self._edge_union_options(edge, new_vertex, cluster, new_cluster):
            string = "{} ∪ {} =".format(cluster, new_cluster) if self.config["print_steps"] else ""
            uC = new_cluster.union(cluster)
            if string:
                print(string, uC)


    def _edge_union_options(self, edge, new_vertex, cluster, new_cluster):
        '''
        Checks the type of the fully grown edge.
        1. if:     Fully grown edge. New vertex is on the old boundary. Find new boundary on vertex
        2. elif:   Edge grown on itself. This cluster is already connected. Cut half-edge
        3. else:   Edge is between two separate clusters. Returns true to perform some function
        '''
        if new_cluster is None or new_cluster.instance != self.code.instance:
            cluster.add_vertex(new_vertex)
            self._cluster_find_vertices(cluster, new_vertex)
        elif new_cluster is cluster:
            if self.config["dynamic_forest"]:
                self._edge_peel(edge)
        else:
            return True
        return False
    """
    ================================================================================================
                                    2(c). Place clusters in buckets
    ================================================================================================
    """
    def _place_bucket(self, place_list, bucket_i):
        for cluster in place_list:
            self._cluster_place_bucket(cluster.find(), bucket_i)

    def _cluster_place_bucket(self, cluster, bucket_i, **kwargs):
        """
        :param cluster      current cluster

        The inputted cluster has undergone a size change, either due to cluster growth or during a cluster merge, in which case the new root cluster is inputted. We increase the appropriate bucket number of the cluster until the fitting bucket has been reached. The cluster is then appended to that bucket.
        If the max bucket number has been reached. The cluster is appended to the wastebucket, which will never be selected for growth.
        """
        if (cluster.parity % 2 == 1 and not cluster.on_bound):
            if self.config["weighted_growth"]:
                cluster.bucket = 2 * (cluster.size - 1) + cluster.support
                self.buckets[cluster.bucket].append(cluster)
                if cluster.bucket > self.bucket_max_filled:
                    self.bucket_max_filled = cluster.bucket
            else:
                self.buckets[0].append(cluster)
                cluster.bucket = bucket_i + 1
        else:
            cluster.bucket = None
    """
    ================================================================================================
                                    3. Peel clusters
    ================================================================================================
    """
    def peel_clusters(self, *args, **kwargs):
        """
        Loops over all vertices to find pendant vertices which are selected from peeling using {peel_edge}

        """
        for layer in self.code.ancilla_qubits.values():
            for vertex in layer.values():
                if vertex.cluster and vertex.cluster.instance == self.code.instance:
                    if not self.config["dynamic_forest"]:
                        self._static_forest(vertex)
                    cluster = self._get_vertex_cluster(vertex)
                    self._peel_leaf(cluster, vertex)

    def _peel_leaf(self, cluster, vertex, *args, **kwargs):
        """
        :param cluster          current active cluster
        :param vertex           pendant vertex of the edge to be peeled

        Recursive function which peels a branch of the tree if the input vertex is a pendant vertex

        If there is only one neighbor of the input vertex that is in the same cluster, this vertex is a pendant vertex and can be peeled. The function calls itself on the other vertex of the edge leaf.
        """
        num_connect = 0
        connect_key = None

        for key in vertex.parity_qubits:
            (new_vertex, edge) = self.get_neighbor(vertex, key)
            if self.support[edge] == 2 and edge.peeled != self.code.instance:
                new_cluster = self._get_vertex_cluster(new_vertex)
                if new_cluster is cluster:
                    num_connect += 1
                    connect_key = key
                if num_connect > 1:
                    break
        else:
            if num_connect == 1:
                (new_vertex, edge) = self.get_neighbor(vertex, connect_key)
                edge.peeled = self.code.instance
                if vertex.measured_state:
                    new_vertex.measured_state = not new_vertex.measured_state
                    self.correct_edge(vertex, connect_key)
                self._peel_leaf(cluster, new_vertex)

    def _static_forest(self, vertex):
        vertex.forest = self.code.instance
        for key in vertex.parity_qubits:
            (new_vertex, edge) = self.get_neighbor(vertex, key)
            if self.support[edge] == 2:
                if new_vertex.forest == self.code.instance:
                    if edge.forest != self.code.instance:
                        self._edge_peel(edge)
                else:
                    edge.forest = self.code.instance
                    self._static_forest(new_vertex)

    """
    ================================================================================================
                                    General helper functions
    ================================================================================================
    """
    def _get_vertex_cluster(self, vertex):
        '''
        Returns the cluster to which the input vertex belongs to.
        '''
        if vertex.cluster is None or vertex.cluster.instance != self.code.instance:
            return None
        else:
            vertex.cluster = vertex.cluster.find()
            return vertex.cluster


    def _cluster_find_vertices(self, cluster, vertex, **kwargs):
        """
        :param cluster          current cluster
        :param vertex           vertex that is recently added to the cluster

        Recursive function which adds all connected erasure edges to a cluster, or finds the boundary on a vertex.

        For a given vertex, this function finds the neighboring edges and vertices that are in the the currunt cluster. Any new vertex or edge will be added to the graph.
        If the newly found edge is part of the erasure, the edge and the corresponding vertex will be added to the cluster, and the function is started again on the new vertex. Otherwise it will be added to the boundary.
        If a vertex is an anyon, its property and the parity of the cluster will be updated accordingly.
        """

        for key in vertex.parity_qubits:
            (new_vertex, edge) = self.get_neighbor(vertex, key)

            if "erasure" in self.code.errors and edge.qubit.erasure == self.code.instance:
                # if edge not already traversed
                if self.support[edge] == 0 and edge.peeled != self.code.instance:
                    if new_vertex.cluster == cluster:   # cycle detected, peel edge
                        self._edge_peel(edge)
                    else:                               # if no cycle detected
                        cluster.add_vertex(new_vertex)
                        self._edge_full(edge)
                        self._cluster_find_vertices(cluster, new_vertex)
            else:
                # Make sure new bound does not lead to self
                if new_vertex.cluster is not cluster:
                    cluster.new_bound.append((vertex, edge, new_vertex))

    def _edge_peel(self, edge):
        edge.peeled = self.code.instance
        self.support[edge] = 0

    def _edge_full(self, edge):
        self.support[edge] = 2


class Planar(Toric):
    """Union-Find decoder for the planar lattice."""

    def _edge_union_options(self, edge, new_vertex, cluster, new_cluster):
        '''
        Checks the type of the fully grown edge.
        1. if:      Edge grown on own cluster or second connection to the boundary. Cut half-edge
        2. elif:    Fully grown edge. New vertex is on the old boundary. Find new boundary on vertex
        3. else:    Edge is between two separate clusters. Returns true to perform some function
        '''

        p_bound =  new_cluster is not None and new_cluster.instance == self.code.instance and new_cluster.on_bound 
        if cluster.on_bound and type(new_vertex) == PseudoQubit:
            if self.config["dynamic_forest"]:
                self._edge_peel(edge)
        elif new_cluster is None or new_cluster.instance != self.code.instance:
            if self.config["print_steps"] and type(new_vertex) == PseudoQubit and not cluster.on_bound:
                print("{} ∪ boundary".format(cluster))
            cluster.add_vertex(new_vertex)
            self._cluster_find_vertices(cluster, new_vertex)
        elif new_cluster is cluster:
            if self.config["dynamic_forest"]:
                self._edge_peel(edge)
        elif cluster.on_bound and p_bound:
            if self.config["dynamic_forest"]:
                self._edge_peel(edge)
            else:
                return True
        else:
            return True
        return False

    def _static_forest(self, vertex, found_bound = False, **kwargs):

        if not found_bound and vertex.cluster.find().parity % 2 == 0:
            found_bound = True

        vertex.forest = self.code.instance
        for key in vertex.parity_qubits:
            (new_vertex, edge) = self.get_neighbor(vertex, key)

            if self.support[edge] == 2:
                
                if type(new_vertex) is PseudoQubit:
                    if found_bound:
                        self._edge_peel(edge)
                    else:
                        edge.forest = self.code.instance
                        found_bound = True
                    continue
                    
                if new_vertex.forest == self.code.instance:
                    if edge.forest != self.code.instance:
                        self._edge_peel(edge)
                else:
                    edge.forest = self.code.instance
                    found_bound = self._static_forest(new_vertex, found_bound = found_bound)
        return found_bound