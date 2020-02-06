import plot_graph_lattice as pg
import random

class toric(object):
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

    def __init__(self, size, decoder, plot_load=False, plot_config=None, type="toric"):

        self.type = type
        self.size = size
        self.decoder = decoder
        self.C = {}
        self.S = {}
        self.B = {}
        self.Q = {}
        self.cID = 0

        self.init_graph(plot_load, plot_config)


    def __repr__(self):

        numC = 0
        for cluster in self.C.values():
            if cluster.parent == cluster:
                numC += 1
        return f"{self.type} graph object with {numC} clusters, {len(self.S)} stabs, {len(self.Q)} qubits and {len(self.B)} boundaries"

    '''
    ########################################################################################

                                    Surface code functions

    ########################################################################################
    '''
    def init_graph(self, plot_load, plot_config):

        for ertype in range(2):
            for y in range(self.size):
                for x in range(self.size):
                    self.add_stab((ertype, y, x))

        # Add edges to self
        for y in range(self.size):
            for x in range(self.size):

                VL, VR = self.S[(0, y, x)], self.S[(0, y, (x + 1) % self.size)]
                VU, VD = self.S[(1, (y - 1) % self.size, x)], self.S[(1, y, x)]
                self.add_qubit(y, x, 0, VL, VR, VU, VD)

                VU, VD = self.S[(0, y, x)], self.S[(0, (y + 1) % self.size, x)]
                VL, VR = self.S[(1, y, (x - 1) % self.size)], self.S[(1, y, x)]
                self.add_qubit(y, x, 1, VL, VR, VU, VD)

        self.plot = pg.lattice_plot(self, **plot_config) if plot_load else None


    def init_erasure(self, pE=0, **kwargs):
        """
        :param pE           probability of an erasure error
        :param savefile     toggle to save the errors to a file

        Initializes an erasure error with probabilty pE, which will take form as a uniformly chosen pauli X and/or Z error.
        """

        if pE != 0:
            for qubit in self.Q.values():
                if random.random() < pE:
                    qubit.erasure = True
                    rand = random.random()
                    if rand < 0.25:
                        qubit.E[0].state = 1 - qubit.E[0].state
                    elif rand >= 0.25 and rand < 0.5:
                        qubit.E[1].state = 1 - qubit.E[1].state
                    elif rand >= 0.5 and rand < 0.75:
                        qubit.E[0].state = 1 - qubit.E[0].state
                        qubit.E[1].state = 1 - qubit.E[1].state

        if self.plot: self.plot.plot_erasures()


    def init_pauli(self, pX=0, pZ=0, **kwargs):
        """
        :param pX           probability of a Pauli X error
        :param pZ           probability of a Pauli Z error
        :param savefile     toggle to save the errors to a file

        initates Pauli X and Z errors on the lattice based on the error rates
        """

        if pX != 0 or pZ != 0:
            for qubit in self.Q.values():
                if pX != 0 and random.random() < pX:
                    qubit.E[0].state = 1 - qubit.E[0].state
                if pZ != 0 and random.random() < pZ:
                    qubit.E[1].state = 1 - qubit.E[1].state

        if self.plot: self.plot.plot_errors()


    def measure_stab(self, **kwargs):
        """
        The measurement outcomes of the stabilizers, which are the vertices on the self are saved to their corresponding vertex objects. We loop over all vertex objects and over their neighboring edge or qubit objects.
        """
        for stab in self.S.values():
            for vertex, edge in stab.neighbors.values():
                if edge.state:
                    stab.state = 1 - stab.state

        if self.plot: self.plot.plot_syndrome()


    def logical_error(self):

        """
        Finds whether there are any logical errors on the lattice/self. The logical error is returned as [Xvertical, Xhorizontal, Zvertical, Zhorizontal], where each item represents a homological Loop
        """

        if self.plot: self.plot.plot_final()

        logical_error = [0, 0, 0, 0]

        for i in range(self.size):
            if self.Q[(i, 0, 0, 0)].E[0].state:
                logical_error[0] = 1 - logical_error[0]
            if self.Q[(0, i, 1, 0)].E[0].state:
                logical_error[1] = 1 - logical_error[1]
            if self.Q[(i, 0, 1, 0)].E[1].state:
                logical_error[2] = 1 - logical_error[2]
            if self.Q[(0, i, 0, 0)].E[1].state:
                logical_error[3] = 1 - logical_error[3]

        errorless = True if logical_error == [0, 0, 0, 0] else False
        return logical_error, errorless

    '''
    ########################################################################################

                                    Constructor functions

    ########################################################################################
    '''

    def add_cluster(self, cID, vertex):
        """Adds a cluster with cluster ID number cID"""
        self.C[cID] = Cluster(cID, vertex)
        return self.C[cID]

    def get_cluster(self, cID, vertex):
        return Cluster(cID, vertex)

    def add_stab(self, sID):
        """Adds a stabilizer with stab ID number sID"""
        self.S[sID] = Stab(sID)
        return self.S[sID]

    def add_boundary(self, sID):
        """Adds a open bounday (stab like) with bounday ID number sID"""
        self.B[sID] = Bound(sID)
        return self.B[sID]

    def add_edge(self, qID):
        self.E[qID] = Edge(qID)
        return self.E[qID]

    def add_qubit(self, y, x, td, VL, VR, VU, VD, z=0):
        """Adds an edge with edge ID number qID with pointers to vertices. Also adds pointers to this edge on the vertices. """

        #(ertype, y, x, td, z, hv)

        qID = (y, x, z, td)
        qubit = Qubit(*qID)
        self.Q[qID] = qubit

        E1, E2 = (qubit.E[0], qubit.E[1]) if td == 0 else (qubit.E[1], qubit.E[0])

        VL.neighbors["r"] = (VR, E1)
        VR.neighbors["l"] = (VL, E1)
        VU.neighbors["d"] = (VD, E2)
        VD.neighbors["u"] = (VU, E2)

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

class planar(toric):
    def __init__(self, *args, **kwargs):
        super().__init__(type="planar", *args, **kwargs)


    def init_graph(self, plot_load, plot_config):

        # Add vertices to self
        for yx in range(self.size):
            for xy in range(self.size - 1):
                self.add_stab((0, yx, xy + 1))
                self.add_stab((1, xy, yx))

            self.add_boundary((0, yx, 0))
            self.add_boundary((0, yx, self.size))
            self.add_boundary((1, -1, yx))
            self.add_boundary((1, self.size - 1, yx))

        for y in range(self.size):
            for x in range(self.size):
                if x == 0:
                    VL, VR = self.B[(0, y, x)], self.S[(0, y, x + 1)]
                elif x == self.size - 1:
                    VL, VR = self.S[(0, y, x)], self.B[(0, y, x + 1)]
                else:
                    VL, VR = self.S[(0, y, x)], self.S[(0, y, x + 1)]
                if y == 0:
                    VU, VD = self.B[(1, y - 1, x)], self.S[(1, y, x)]
                elif y == self.size - 1:
                    VU, VD = self.S[(1, y - 1, x)], self.B[(1, y, x)]
                else:
                    VU, VD = self.S[(1, y - 1, x)], self.S[(1, y, x)]

                self.add_qubit(y, x, 0, VL, VR, VU, VD)

                if y != self.size - 1 and x != self.size - 1:
                    VU, VD = self.S[(0, y, x + 1)], self.S[(0, y + 1, x + 1)]
                    VL, VR = self.S[(1, y, x)], self.S[(1, y, x + 1)]
                    self.add_qubit(y, x + 1, 1, VL, VR, VU, VD)

        self.plot = pg.lattice_plot(self, **plot_config) if plot_load else None


    def logical_error(self):

        if self.plot: self.plot.plot_final()

        logical_error = [False, False]

        for i in range(self.size):
            if self.Q[(i, 0, 0, 0)].E[0].state:
                logical_error[0] = 1 - logical_error[0]
            if self.Q[(0, i, 0, 0)].E[1].state:
                logical_error[1] = 1 - logical_error[1]

        errorless = True if logical_error == [0, 0] else False
        return logical_error, errorless

'''
########################################################################################

                            Subclasses: Graph objects

########################################################################################
'''

class Cluster(object):
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


class Stab(object):
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


class Bound(Stab):
    def __init__(self, sID):
        super().__init__(sID, type=1)

    def __repr__(self):
        type = "X" if self.sID[0] == 0 else "Z"
        return "b" + type + "(" + str(self.sID[1]) + "," + str(self.sID[2]) + ")"


class Qubit(object):
    def __init__(self, y, x, z, td):
        self.qID = (y, x, z, td)
        self.erasure = 0
        self.E = [Edge(self, ertype=0), Edge(self, ertype=1)]

    def __repr__(self):
        return "q({},{},{}:{})".format(*self.qID)

    def reset(self):
        self.erasure = 0
        self.E[0].reset()
        self.E[1].reset()


class Edge(object):
    """
    Edge object with parameters:
    qID         (ertype, y, x, z, td, hv)

    erasure     boolean of erased edge
    vertices    tuple of the two conected vertices
    state       boolean indicating the state of the qubit
    cluster     Cluster object of which this edge is apart of
    peeled      boolean indicating whether this edge has peeled
    matching    boolean indicating whether this edge is apart of the matching
    """

    def __init__(self, qubit, ertype, hv=0):
        # fixed parameters
        self.qubit = qubit
        self.eID = (ertype, hv)

        # iteration parameters
        self.cluster    = None
        self.erasure    = 0
        self.state      = 0
        self.support    = 0
        self.peeled     = 0
        self.matching   = 0

    def __repr__(self):
        errortype = "X" if self.eID[0] == 0 else "Z"
        orientation = "-" if self.eID[0] == self.qubit.qID[3] else "|"
        hvtype = "e" if self.eID[1] == 0 else "v"
        coordinate = self.qubit.qID[:3]
        return "{}{}{}({},{},{})".format(hvtype, errortype, orientation, *coordinate)

    def reset(self):
        """
        Changes all iteration paramters to their initial value
        """
        self.cluster    = None
        self.erasure    = 0
        self.state      = 0
        self.support    = 0
        self.peeled     = 0
        self.matching   = 0
