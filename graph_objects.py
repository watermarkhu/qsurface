class iGraph(object):
    """
    The graph in which the vertices, edges and clusters exist. Has the following parameters

    C           dict of clusters with
                    Key:    cID number
                    Value:  Cluster object
    S           dict of stabilizers with
                    Key:    sID number
                    Value:  Stab object
    B           dict of open boundaries with
                    Key:    sID number
                    Value:  Boundary object
    Q           dict of qubits with
                    Key:    qID number
                    Value:  Qubit object with two Edge objects
    wind        dict keys from the possible directions of neighbors.

    """

    def __init__(self, size, type, decoder):
        self.size = size
        self.type = type
        self.decoder = decoder
        self.C = {}
        self.S = {}
        self.B = {}
        self.Q = {}
        self.cID = 0
        self.wind = ["u", "d", "l", "r"]
        self.plot = None

    def __repr__(self):

        numC = 0
        for cluster in self.C.values():
            if cluster.parent == cluster:
                numC += 1
        return (
            "Graph object with "
            + str(numC)
            + " Clusters, "
            + str(len(self.S))
            + " Stabilizers,  "
            + str(len(self.Q))
            + " Qubits and "
            + str(len(self.B))
            + " Boundaries"
        )

    def add_cluster(self, cID, vertex):
        """Adds a cluster with cluster ID number cID"""
        self.C[cID] = iCluster(cID, vertex)
        return self.C[cID]

    def get_cluster(self, cID, vertex):
        return iCluster(cID, vertex)

    def add_stab(self, sID):
        """Adds a stabilizer with stab ID number sID"""
        self.S[sID] = iStab(sID)
        return self.S[sID]

    def add_boundary(self, sID):
        """Adds a open bounday (stab like) with bounday ID number sID"""
        self.B[sID] = iBoundary(sID)
        return self.B[sID]

    def add_qubit(self, qID, VL, VR, VU, VD):
        """Adds an edge with edge ID number qID with pointers to vertices. Also adds pointers to this edge on the vertices. """

        qubit = iQubit(qID)
        self.Q[qID] = qubit
        E1, E2 = (qubit.VXE, qubit.PZE) if qID[2] == 0 else (qubit.PZE, qubit.VXE)
        VL.neighbors["r"] = (VR, E1)
        VR.neighbors["l"] = (VL, E1)
        VU.neighbors["d"] = (VD, E2)
        VD.neighbors["u"] = (VU, E2)

        return qubit

    def reset(self):
        """
        Resets the graph by deleting all clusters and resetting the edges and vertices

        """
        self.C, self.cID = {}, 0
        for qubit in self.Q.values():
            qubit.reset()
        for stab in self.S.values():
            stab.reset()
        for bound in self.B.values():
            bound.reset()

        # if self.plot: self.plot.init_plot()
        # if self.decoder.plot: self.decoder.plot.init_plot()


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

    def __init__(self, cID, vertex):
        # self.inf = {"cID": cID, "size": 0, "parity": 0}
        self.cID = cID
        self.size = 0
        self.parity = 0
        self.parent = self
        self.childs = [[], []]
        self.boundary = [[], []]
        self.bucket = 0
        self.support = 0

        '''
        planar
        '''
        self.on_bound = 0

        '''
        Evengrow
        '''
        self.root_node = vertex.node
        self.calc_delay = []
        self.mindl = 0
        self.add_vertex(vertex)

    def __repr__(self):
        return "C" + str(self.cID) + "(" + str(self.size) + ":" + str(self.parity) + ")"

    def add_vertex(self, vertex):
        """Adds a stabilizer to a cluster. Also update cluster value of this stabilizer."""
        self.size += 1
        if vertex.state:
            self.parity += 1
        vertex.cluster = self


class iStab(object):
    """
    Stab object with parameters:
    sID         location of stabilizer (ertype, y, x)
    neighbors   dict of the neighobrs (in the graph) of this stabilizer with
                    Key:    wind
                    Value   (Stab object, Edge object)
    state       boolean indicating anyon state of stabilizer
    cluster     Cluster object of which this stabilizer is apart of
    tree        boolean indicating whether this stabilizer has been traversed
    """

    def __init__(self, sID, type=0):
        # fixed paramters
        self.type = type
        self.sID = sID
        self.neighbors = {}

        # iteration parameters
        self.state = 0
        self.cluster = None
        self.tree = 0

        '''
        DGvertices
        '''
        self.count = 0

        '''
        Evengrow
        '''
        self.node = None
        self.new_bound = []

    def __repr__(self):
        type = "X" if self.sID[0] == 0 else "Z"
        return "v" + type + "(" + str(self.sID[1]) + "," + str(self.sID[2]) + ")"

    def reset(self):
        """
        Changes all iteration paramters to their initial value
        """
        self.state = 0
        self.cluster = None
        self.tree = 0
        self.node = None


class iBoundary(iStab):
    def __init__(self, sID):
        super().__init__(sID, type=1)

    def __repr__(self):
        type = "X" if self.sID[0] == 0 else "Z"
        return "b" + type + "(" + str(self.sID[1]) + "," + str(self.sID[2]) + ")"


class iQubit(object):

    def __init__(self, qID):
        self.qID = qID
        self.erasure = 0
        self.VXE = iEdge((0, qID[2]), self)
        self.PZE = iEdge((1, 1 - qID[2]), self)

    def __repr__(self):
        return "q({},{}:{})".format(*self.qID)

    def reset(self):
        self.erasure = 0
        self.VXE.reset()
        self.PZE.reset()


class iEdge(object):
    """
    Edge object with parameters:
    type        type of this edge: 0 for X type connecting vertices, 1 for Z type connecting plaquettes
    vertices    tuple of the two conected vertices
    state       boolean indicating the state of the qubit
    cluster     Cluster object of which this edge is apart of
    peeled      boolean indicating whether this edge has peeled
    matching    boolean indicating whether this edge is apart of the matching
    """

    def __init__(self, type, qubit):
        # fixed parameters
        self.type = type
        self.qubit = qubit

        # iteration parameters
        self.cluster = None
        self.state = 0
        self.support = 0
        self.peeled = 0
        self.matching = 0

    def __repr__(self):
        errortype = "X" if self.type[0] == 0 else "Z"
        orientation = "-" if self.type[1] == 0 else "|"
        return "e{}{}({},{},{})".format(errortype, orientation, *self.qubit.qID)

    def reset(self):
        """
        Changes all iteration paramters to their initial value
        """
        self.cluster = None
        self.state = 0
        self.support = 0
        self.peeled = 0
        self.matching = 0

    def grow_reset(self):
        self.cluster = None
        self.support = 0
        self.peeled = 0
