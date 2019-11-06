class iGraph(object):
    """
    The graph in which the vertices, edges and clusters exist. Has the following parameters

    C           dict of clusters with
                    Key:    cID number
                    Value:  Cluster object
    V           dict of vertices with
                    Key:    sID number
                    Value:  Vertex object
    E           dict of edges with
                    Key:    qID number
                    Value:  Edge object
    wind        dict keys from the possible directions of neighbors.

    """

    def __init__(self, size):
        self.size = size
        self.C = {}
        self.V = {}
        self.E = {}
        self.wind = ["u", "d", "l", "r"]

    def __repr__(self):

        numC = 0
        for cluster in self.C.values():
            if cluster.parent == cluster:
                numC += 1
        return (
            "Graph object with "
            + str(numC)
            + " Clusters, "
            + str(len(self.V))
            + " Vertices and "
            + str(len(self.E))
            + " Edges."
        )

    def add_cluster(self, cID):
        """Adds a cluster with cluster ID number cID"""
        self.C[cID] = iCluster(cID)
        return self.C[cID]

    def add_vertex(self, sID):
        """Adds a vertex with vertex ID number sID"""
        self.V[sID] = iVertex(sID)
        return self.V[sID]

    def add_edge(self, qID, sIDlu, sIDrd, orientation):
        """Adds an edge with edge ID number qID with pointers to vertices. Also adds pointers to this edge on the vertices. """

        V1 = self.V[sIDlu]
        V2 = self.V[sIDrd]
        E = iEdge(qID)
        self.E[qID] = E
        if orientation == "H":
            V1.neighbors["r"] = (V2, E)
            V2.neighbors["l"] = (V1, E)
        elif orientation == "V":
            V1.neighbors["d"] = (V2, E)
            V2.neighbors["u"] = (V1, E)
        return E

    def reset(self):
        """
        Resets the graph by deleting all clusters and resetting the edges and vertices

        """
        self.C = {}
        for edge in self.E.values():
            edge.reset()
        for vertex in self.V.values():
            vertex.reset()

    def print_graph_stop(self, clusters=None, prestring="", printmerged=1):
        """
        :param clusters     either None or a list of clusters
        :param prestring    string to print before evertything else

        This function prints a cluster's size, parity, growth state and appropiate bucket number. If None is inputted, all clusters will be displayed.
        """
        printend = 0
        if clusters is None:
            clusters, printend = list(self.C.values()), 0
            print("Showing all clusters:")

        for cluster in clusters:

            if cluster.parent == cluster:
                print(prestring + str(cluster), end="")
                print(" with size: " + str(cluster.size), end="")
                print(", parity: " + str(cluster.parity), end="")
                print(", support: " + str(cluster.support), end="")
                if cluster.bucket is None:
                    print(", and bucket: " + str(cluster.bucket))
                else:
                    if cluster.bucket < self.numbuckets:
                        print(", and bucket: " + str(cluster.bucket))
                    else:
                        print(", and bucket: wastebasket")
            elif printmerged:
                print(str(cluster), "is merged with", str(cluster.parent))
        if printend:
            print("")


class iCluster(object):
    """
    Cluster obejct with parameters:
    cID         ID number of cluster
    size        size of this cluster based on the number contained vertices
    parity      parity of this cluster based on the number of contained anyons
    parent      the parent cluster of this cluster
    childs      the children clusters of this cluster
    full_edged  growth state of the cluster: 1 if False, 2 if True
    full_bound  boundary for growth step 1
    half_bound  boundary for growth step 2
    bucket      the appropiate bucket number of this cluster

    """

    def __init__(self, cID):
        # self.inf = {"cID": cID, "size": 0, "parity": 0}
        self.cID = cID
        self.size = 0
        self.parity = 0
        self.parent = self
        self.childs = [[], []]
        self.boundary = [[], []]
        self.bucket = 0
        self.support = 0

    def __repr__(self):
        return "C" + str(self.cID) + "(" + str(self.size) + ":" + str(self.parity) + ")"

    def add_vertex(self, vertex):
        """Adds a vertex to a cluster. Also update cluster value of this vertex."""
        self.size += 1
        if vertex.state:
            self.parity += 1
        vertex.cluster = self


class iVertex(object):
    """
    Vertex object with parameters:
    sID         location of vertex (ertype, y, x)
    neighbors   dict of the neighobrs (in the graph) of this vertex with
                    Key:    wind
                    Value   (Vertex object, Edge object)
    state       boolean indicating anyon state of vertex
    cluster     Cluster object of which this vertex is apart of
    tree        boolean indicating whether this vertex has been traversed
    """

    def __init__(self, sID):
        # fixed paramters
        self.sID = sID
        self.neighbors = {}

        # iteration parameters
        self.state = False
        self.cluster = None
        self.tree = False

    def __repr__(self):
        type = "X" if self.sID[0] == 0 else "Z"
        return "v" + type + "(" + str(self.sID[1]) + "," + str(self.sID[2]) + ")"

    def reset(self):
        """
        Changes all iteration paramters to their initial value
        """
        self.state = False
        self.cluster = None
        self.tree = False


class iEdge(object):
    """
    Edge object with parameters:
    qID         location of qubit/edge (ertype, y, x, td)
    vertices    tuple of the two conected vertices
    state       boolean indicating the state of the qubit
    cluster     Cluster object of which this edge is apart of
    peeled      boolean indicating whether this edge has peeled
    matching    boolean indicating whether this edge is apart of the matching
    """

    def __init__(self, qID):
        # fixed parameters
        self.qID = qID

        # iteration parameters
        self.cluster = None
        self.state = 0
        self.erasure = 0
        self.support = 0
        self.peeled = 0
        self.matching = 0

    def __repr__(self):
        if self.qID[0] == 0:
            errortype = "X"
            edgetype = "-" if self.qID[3] == 0 else "|"
        else:
            errortype = "Z"
            edgetype = "|" if self.qID[3] == 0 else "-"
        return (
            "e"
            + errortype
            + edgetype
            + "("
            + str(self.qID[1])
            + ","
            + str(self.qID[2])
            + ")"
        )

    def reset(self):
        """
        Changes all iteration paramters to their initial value
        """
        self.cluster = None
        self.state = 0
        self.erasure = 0
        self.support = 0
        self.peeled = 0
        self.matching = 0


def init_toric_graph(size):

    graph = iGraph(size)

    # Add vertices to graph
    for ertype in range(2):
        for y in range(size):
            for x in range(size):
                graph.add_vertex((ertype, y, x))

    # Add edges to graph
    for ertype in range(2):
        for y in range(size):
            for x in range(size):
                for td in range(2):
                    qID = (ertype, y, x, td)
                    if ertype == 0 and td == 0:
                        VL_sID = (ertype, y, x)
                        VR_sID = (ertype, y, (x + 1) % size)
                        graph.add_edge(qID, VL_sID, VR_sID, "H")
                    elif ertype == 1 and td == 1:
                        VL_sID = (ertype, y, (x - 1) % size)
                        VR_sID = (ertype, y, x)
                        graph.add_edge(qID, VL_sID, VR_sID, "H")
                    elif ertype == 0 and td == 1:
                        VU_sID = (ertype, y, x)
                        VD_sID = (ertype, (y + 1) % size, x)
                        graph.add_edge(qID, VU_sID, VD_sID, "V")
                    elif ertype == 1 and td == 0:
                        VU_sID = (ertype, (y - 1) % size, x)
                        VD_sID = (ertype, y, x)
                        graph.add_edge(qID, VU_sID, VD_sID, "V")

    return graph
