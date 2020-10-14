from opensurfacesim.codes.elements import Edge
from .._template import SimCode


class Cluster(object):
    """
    Cluster object with parameters:
    cID         ID number of cluster
    size        size of this cluster based on the number contained vertices
    parity      parity of this cluster based on the number of contained anyons
    parent      the parent cluster of this cluster
    childs      the children clusters of this cluster
    boundary    len(2) list containing 1) current boundary, 2) next boundary
    bucket      the appropiate bucket number of this cluster
    support     growth state of the cluster: 1 if False, 2 if True

    [planar]
    on_bound    whether this clusters is connected to the boundary

    """
    def __init__(self, index, instance, **kwargs):
        # self.inf = {"cID": cID, "size": 0, "parity": 0}
        self.index      = index
        self.instance   = instance
        self.size       = 0
        self.parity     = 0
        self.parent     = self
        self.children   = [[], []]
        self.boundary   = [[], []]
        self.bucket     = 0
        self.support    = 0
        self.on_bound   = 0

    def __repr__(self):
        return "C" + str(self.index) + "(" + str(self.size) + ":" + str(self.parity) + ")"

    def __hash__(self):
        return self.index, self.instance

    def add_vertex(self, vertex):
        """Adds a stabilizer to a cluster. Also update cluster value of this stabilizer."""
        self.size += 1
        if vertex.measured_state:
            self.parity += 1
        vertex.cluster = self


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
        self.boundary[0].extend(cluster.boundary[0])   
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
        erasure=True,
    )

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.config["step_growth"] = not (self.config["step_bucket"] or self.config["step_cluster"])
        self.code.ancillaQubit.cluster = None
        self.code.edge.peeled = None

        self.support = {}
        for layer in self.code.data_qubits.values():
            for data_qubit in layer.values():
                for edge in data_qubit.edges.values():
                    self.support[edge] = 0
        if hasattr(self.code, "pseudo_edges"):
            for edge in self.code.pseudo_edges:
                self.support[edge] = 0

        if self.config["weighted_growth"]:
            self.buckets_num = self.code.size[0]*self.code.size[1]*self.code.layers//2
        else:
            self.buckets_num = 2

    def do_decode(self, **kwargs):
        # Inherited docstrings
        self.buckets = [[] for _ in range(self.buckets_num)]
        self.bucket_max_filled = 0
        self.cluster_index = 0
        self.clusters, self.place, self.fusion = [], [], []

        self.find_clusters(**kwargs)
        self.grow_clusters(**kwargs)                          
        # self.peel_clusters(**kwargs)
        self.clean_up()

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
            if vertex.cluster is None:
                cluster = Cluster(self.cluster_index, self.code.instance)
                cluster.add_vertex(vertex)
                self._cluster_find_vertices(cluster, vertex)
                self._cluster_place_bucket(cluster)
                self.cluster_index += 1
                self.clusters.append(cluster)

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

        if self.config["print_steps"]:
            self.show_clusters_state()

        for bucket_i, bucket in enumerate(self.buckets[start_bucket:], start_bucket):
            if bucket_i > self.bucket_max_filled:
                break
            if not bucket:  # no need to check empty bucket
                continue

            place = self._grow_bucket(bucket, bucket_i)
            self._fuse_bucket(place)
            for cluster in place:
                self._cluster_place_bucket(cluster.find())

            if self.config["print_steps"]:
                self.show_clusters_state(printmerged=False)

    def _grow_bucket(self, bucket, bucket_i, **kwargs):
        '''
        Grows the clusters which are contained in the current bucket.
        Skips the cluster if it is already contained in a higher bucket or if the support parameters does not equal the current bucket support
        '''
        self.fusion, place = [], []  # Initiate Fusion list
        while bucket:  # Loop over all clusters in the current bucket\
            cluster = bucket.pop().find()
            if cluster.bucket == bucket_i and cluster.support == bucket_i % 2:
                place.append(cluster)
                cluster.support = 1 - cluster.support
                self._grow_boundary(cluster)
        return place

                
    def _grow_boundary(self, cluster, **kwargs):
        '''
        Grows the boundary list that is stored at the current cluster.
        Fully grown edges are added to the fusion list.
        '''
        cluster.boundary = [[], cluster.boundary[0]]     # Set boundary

        while cluster.boundary[1]:                       # grow boundary
            bound = cluster.boundary[1].pop()
            vertex, new_edge, _ = bound

            if self.support[new_edge] != 2:              # if not already fully grown
                self.support[new_edge] += 1              # Grow boundaries by half-edge
                if self.support[new_edge] == 2:          # if edge is fully grown
                    self.fusion.append(bound)            # Append to fusion list of edges
                else:
                    cluster.boundary[0].append(bound)

    """
    ================================================================================================
                                    2(b). Grow clusters fusion
    ================================================================================================
    """
    def _fuse_bucket(self, bucket_i, **kwrags):
        '''
        Put clusters in new buckets. Some will be added double, but will be skipped by the new_boundary check.

        Fuse all edges in the fusion list by considering the vertex connectivity degeneracy.
        During a union of two clusters, there may be multiple edges in the fusion list that connect these clusters. We loop over all edges to count the number of fusion edges that is connected to the nodes involved. Fusion edges that are connected to vertices with high fusion edge connectivity equals a higher degeneracy in the number of edges to connect two clusters.
        We order the fusion edges by this vertex connectivity degeneracy and grows the largest degenerate edges first.
        '''
        if self.config["degenerate_fusion"]:

            merging = []
            for aV, edge, pV in self.fusion:
                aC = self._get_vertex_cluster(aV)
                pC = self._get_vertex_cluster(pV)

                '''
                if:     Fully grown edge. New vertex is on the old boundary. Find new boundary on vertex
                elif:   Edge grown on itself. This cluster is already connected. Cut half-edge
                else:   Clusters merge by weighted union
                '''
                if self._edge_growth_choices(edge, aV, pV, aC, pC):
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
                    self._fully_grown_edge(*items)
        else:
            for aV, edge, pV in self.fusion:
                self._fully_grown_edge(edge, aV, pV)


    def _fully_grown_edge(self, edge, aV, pV, *args, **kwargs):
        '''
        Performs union of two clusters (belonging to aV and pV vertices) on a fully grown edge if its eligible.
        '''
        aC = self._get_vertex_cluster(aV)
        pC = self._get_vertex_cluster(pV)

        if self._edge_growth_choices(edge, aV, pV, aC, pC):
            pC.union(aC)


    def _edge_growth_choices(self, edge, aV, pV, aC, pC):
        '''
        Checks the type of the fully grown edge.
        1. if:     Fully grown edge. New vertex is on the old boundary. Find new boundary on vertex
        2. elif:   Edge grown on itself. This cluster is already connected. Cut half-edge
        3. else:   Edge is between two separate clusters. Returns true to perform some function
        '''
        if pC is None:
            aC.add_vertex(pV)
            self._cluster_find_vertices(aC, pV)
        elif pC is aC:
            self._edge_peel(edge)
        else:
            return True
        return False
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
                    new_vertex.state = not new_vertex.state
                    self.correct_edge(vertex, connect_key)
                self._peel_leaf(cluster, new_vertex)

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

            if edge.qubit.erasure == self.code.instance:
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
                    cluster.boundary[0].append((vertex, edge, new_vertex))


    def _cluster_place_bucket(self, cluster, **kwargs):
        """
        :param cluster      current cluster

        The inputted cluster has undergone a size change, either due to cluster growth or during a cluster merge, in which case the new root cluster is inputted. We increase the appropiate bucket number of the cluster intil the fitting bucket has been reached. The cluster is then appended to that bucket.
        If the max bucket number has been reached. The cluster is appended to the wastebucket, which will never be selected for growth.
            """

        if self.config["weighted_growth"]:
            cluster.bucket = 2 * (cluster.size - 1) + cluster.support
            if (cluster.parity % 2 == 1 and not cluster.on_bound) and cluster.bucket < self.buckets_num:
                self.buckets[cluster.bucket].append(cluster)
                if cluster.bucket > self.bucket_max_filled:
                    self.bucket_max_filled = cluster.bucket
            else:
                cluster.bucket = None
        else:
            if (cluster.parity % 2 == 1 and not cluster.on_bound) and cluster.bucket == 0:
                self.buckets[-1].append(cluster)
                cluster.bucket = 1


    def _edge_peel(self, edge):
        edge.peeled = self.code.instance
        self.support[edge] = 0

    def _edge_full(self, edge):
        self.support[edge] = 2

    def clean_up(self):
        self.support = {edge: 0 for edge in self.support}


    """
    ================================================================================================
                                            Information
    ================================================================================================
    """
    def show_clusters_state(self, clusters=None, prestring="", poststring="", printmerged=1, include_even=0, show=True):
        """
        :param clusters     either None or a list of clusters
        :param prestring    string to print before evertything else

        This function prints a cluster's size, parity, growth state and appropriate bucket number. If None is inputted, all clusters will be displayed.
        """
        string = ""
        if clusters is None:
            clusters = self.clusters
            string += "Showing all clusters:\n" if include_even else "Showing active clusters:\n"

        for cluster in clusters:
            if include_even or (not include_even and cluster.bucket is not None):
                if cluster.parent == cluster:
                    string += prestring + f"{cluster} (S{cluster.support},"
                    string += f"B{cluster.bucket}" if cluster.bucket is not None else "B_"
                    string += f",{cluster.on_bound})" if self.code.name == "planar" else ")"

                    if cluster.cID != clusters[-1].cID: string += "\n"
                elif printmerged:
                    string += str(cluster) + " is merged with " + str(cluster.parent) + ""
                    if cluster is not clusters[-1]: string += "\n"
        string += "\n" + poststring
        if show:
            print(string)
        return string