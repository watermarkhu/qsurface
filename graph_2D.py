import plot_graph_lattice as pgl
import plot_unionfind as puf
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

    def __init__(self, size, decoder, plot2D=0, plot_config={}, *args, **kwargs):

        self.size = size
        self.range = range(size)
        self.decoder = decoder
        decoder.graph = self
        self.decode_layer = 0
        self.C = {}
        self.S = {}
        self.Q = {}
        self.cID = 0
        self.dim = 2
        self.matching_weight = 0

        self.init_graph_layer()

        self.plot2D = plot2D
        self.plot_config = plot_config
        self.gl_plot = pgl.plot_2D(self, **plot_config) if plot2D else None

    def __repr__(self):
        return f"2D {self.__class__.__name__} graph object with"

    def init_uf_plot(self):
        self.uf_plot = puf.plot_2D(self, **self.plot_config)
        return self.uf_plot

    '''
    ########################################################################################

                                    Surface code functions

    ########################################################################################
    '''

    def init_graph_layer(self, z=0):

        self.dirs = ["n", "s", "e", "w"]
        self.S[z], self.Q[z], = {}, {}

        for ertype in [0,1]:
            for y in self.range:
                for x in self.range:
                    self.add_stab(ertype, y, x, z)

        # Add edges to self
        for y in self.range:
            for x in self.range:

                vW, vE = self.S[z][(0, y, x)], self.S[z][(0, y, (x + 1) % self.size)]
                vN, vS = self.S[z][(1, (y - 1) % self.size, x)], self.S[z][(1, y, x)]
                self.add_qubit(0, y, x, z, vW, vE, vN, vS)

                vN, vS = self.S[z][(0, y, x)], self.S[z][(0, (y + 1) % self.size, x)]
                vW, vE = self.S[z][(1, y, (x - 1) % self.size)], self.S[z][(1, y, x)]
                self.add_qubit(1, y, x, z, vW, vE, vN, vS)


    def apply_and_measure_errors(self, pX=0, pZ=0, pE=0, **kwargs):

            self.init_erasure(pE=pE)
            self.init_pauli(pX=pX, pZ=pZ)         # initialize errors
            self.measure_stab()                       # Measure stabiliziers


    def init_erasure(self, pE=0, **kwargs):
        """
        :param pE           probability of an erasure error
        :param savefile     toggle to save the errors to a file

        Initializes an erasure error with probabilty pE, which will take form as a uniformly chosen pauli X and/or Z error.
        """

        if pE == 0:
            return

        for qubit in self.Q[0].values():
            if random.random() < pE:
                qubit.erasure = True
                rand = random.random()
                if rand < 0.25:
                    qubit.E[0].state = 1
                elif rand >= 0.25 and rand < 0.5:
                    qubit.E[1].state = 1
                elif rand >= 0.5 and rand < 0.75:
                    qubit.E[0].state = 1
                    qubit.E[1].state = 1

        if self.gl_plot: self.gl_plot.plot_erasures()


    def init_pauli(self, pX=0, pZ=0, **kwargs):
        """
        :param pX           probability of a Pauli X error
        :param pZ           probability of a Pauli Z error
        :param savefile     toggle to save the errors to a file

        initates Pauli X and Z errors on the lattice based on the error rates
        """

        for qubit in self.Q[0].values():
            if pX != 0 and random.random() < pX:
                qubit.E[0].state = 1
            if pZ != 0 and random.random() < pZ:
                qubit.E[1].state = 1

        if self.gl_plot: self.gl_plot.plot_errors()


    def measure_stab(self, **kwargs):
        """
        The measurement outcomes of the stabilizers, which are the vertices on the self are saved to their corresponding vertex objects. We loop over all vertex objects and over their neighboring edge or qubit objects.
        """
        for stab in self.S[0].values():
            for dir in self.dirs:
                if dir in stab.neighbors:
                    vertex, edge = stab.neighbors[dir]
                    if edge.state:
                        stab.parity = 1 - stab.parity
                    stab.state = stab.parity

        if self.gl_plot: self.gl_plot.plot_syndrome()


    def logical_error(self, z=0):

        """
        Finds whether there are any logical errors on the lattice/self. The logical error is returned as [Xvertical, Xhorizontal, Zvertical, Zhorizontal], where each item represents a homological Loop
        """

        if self.gl_plot: self.gl_plot.plot_final()

        logical_error = [0, 0, 0, 0]

        for i in self.range:
            if self.Q[z][(0, i, 0)].E[0].state:
                logical_error[0] = 1 - logical_error[0]
            if self.Q[z][(1, 0, i)].E[0].state:
                logical_error[1] = 1 - logical_error[1]
            if self.Q[z][(1, i, 0)].E[1].state:
                logical_error[2] = 1 - logical_error[2]
            if self.Q[z][(0, 0, i)].E[1].state:
                logical_error[3] = 1 - logical_error[3]

        errorless = True if logical_error == [0, 0, 0, 0] else False
        return logical_error, errorless


    def count_matching_weight(self, z=0):
        '''
        Loops through all qubits on the layer and counts the number of matchings edges
        '''
        for qubit in self.Q[z].values():
            if qubit.E[0].matching == 1:
                self.matching_weight += 1
            if qubit.E[1].matching == 1:
                self.matching_weight += 1

    '''
    ########################################################################################

                                    Constructor functions

    ########################################################################################
    '''

    def add_cluster(self, cID, vertex):
        """Adds a cluster with cluster ID number cID"""
        cluster = self.C[cID] = Cluster(cID, vertex)
        return cluster

    def get_cluster(self, cID, vertex):
        return Cluster(cID, vertex)

    def add_stab(self, ertype, y, x, z):
        """Adds a stabilizer with stab ID number sID"""
        stab = self.S[z][(ertype, y, x)] = Stab(sID=(ertype, y, x), z=z)
        return stab

    def add_boundary(self, ertype, y, x, z):
        """Adds a open bounday (stab like) with bounday ID number sID"""
        bound = self.B[z][(ertype, y, x)] = Bound(sID=(ertype, y, x), z=z)
        return bound

    def add_qubit(self, td, y, x, z, vW, vE, vN, vS):
        """Adds an edge with edge ID number qID with pointers to vertices. Also adds pointers to this edge on the vertices. """

        qubit = self.Q[z][(td, y, x)] = Qubit(qID=(td, y, x), z=z)
        E1, E2 = (qubit.E[0], qubit.E[1]) if td == 0 else (qubit.E[1], qubit.E[0])

        vW.neighbors["e"] = (vE, E1)
        vE.neighbors["w"] = (vW, E1)
        vN.neighbors["s"] = (vS, E2)
        vS.neighbors["n"] = (vN, E2)

    def reset(self):
        """
        Resets the graph by deleting all clusters and resetting the edges and vertices

        """
        self.C, self.cID = {}, 0
        for qlayer in self.Q.values():
            for qubit in qlayer.values():
                qubit.reset()
        for slayer in self.S.values():
            for stab in slayer.values():
                stab.reset()

'''
########################################################################################

                                        Planar class

########################################################################################
'''

class planar(toric):
    def __init__(self, *args, **kwargs):
        self.B = {}
        super().__init__(*args, **kwargs)

    def init_graph_layer(self, z=0):

        self.dirs = ["n", "s", "e", "w"]
        self.S[z], self.Q[z], self.B[z]= {}, {}, {}

        # Add vertices to self
        for yx in self.range:
            for xy in range(self.size - 1):
                self.add_stab(0, yx, xy + 1, z)
                self.add_stab(1, xy, yx, z)

            self.add_boundary(0, yx, 0, z)
            self.add_boundary(0, yx, self.size, z)
            self.add_boundary(1, -1, yx, z)
            self.add_boundary(1, self.size - 1, yx, z)

        for y in self.range:
            for x in self.range:
                if x == 0:
                    vW, vE = self.B[z][(0, y, x)], self.S[z][(0, y, x + 1)]
                elif x == self.size - 1:
                    vW, vE = self.S[z][(0, y, x)], self.B[z][(0, y, x + 1)]
                else:
                    vW, vE = self.S[z][(0, y, x)], self.S[z][(0, y, x + 1)]
                if y == 0:
                    vN, vS = self.B[z][(1, y - 1, x)], self.S[z][(1, y, x)]
                elif y == self.size - 1:
                    vN, vS = self.S[z][(1, y - 1, x)], self.B[z][(1, y, x)]
                else:
                    vN, vS = self.S[z][(1, y - 1, x)], self.S[z][(1, y, x)]

                self.add_qubit(0, y, x, z, vW, vE, vN, vS)

                if y != self.size - 1 and x != self.size - 1:
                    vN, vS = self.S[z][(0, y, x + 1)], self.S[z][(0, y + 1, x + 1)]
                    vW, vE = self.S[z][(1, y, x)], self.S[z][(1, y, x + 1)]
                    self.add_qubit(1, y, x + 1, z, vW, vE, vN, vS)


    def logical_error(self, z=0):

        if self.gl_plot: self.gl_plot.plot_final()

        logical_error = [0, 0]

        for i in self.range:
            if self.Q[z][(0, i, 0)].E[0].state:
                logical_error[0] = 1 - logical_error[0]
            if self.Q[z][(0, 0, i)].E[1].state:
                logical_error[1] = 1 - logical_error[1]

        errorless = True if logical_error == [0, 0] else False
        return logical_error, errorless


    def reset(self):
        super().reset()
        for layer in self.B.values():
            for bound in layer.values():
                bound.reset()

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

    def __init__(self, sID, type=0, z=0):
        # fixed paramters
        self.type       = type
        self.sID        = sID
        self.z          = z
        self.neighbors  = {}

        # iteration parameters
        self.state      = 0
        self.mstate     = 0
        self.parity     = 0
        self.cluster    = None
        self.tree       = 0

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
        return "v{}({},{}|{})".format(type, *self.sID[1:], self.z)

    def reset(self):
        """
        Changes all iteration paramters to their initial value
        """
        self.state      = 0
        self.mstate     = 0
        self.parity     = 0
        self.cluster    = None
        self.tree       = 0
        self.node       = None


class Bound(Stab):
    def __init__(self, sID, z=0):
        super().__init__(sID, type=1, z=z)

    def __repr__(self):
        type = "X" if self.sID[0] == 0 else "Z"
        return "b{}({},{}|{})".format(type, *self.sID[1:], self.z)


class Qubit(object):
    def __init__(self, qID, z=0):
        '''
        qID         (td, y, x)
        erasure     boolean of erased edge
        '''

        self.qID = qID       # (y, x, z, td)
        self.z = z
        self.erasure = 0
        self.E = [Edge(self, ertype=0, z=z), Edge(self, ertype=1, z=z)]

    def __repr__(self):
        return "q({},{}:{}|{})".format(*self.qID[1:], self.qID[0], self.z)

    def reset(self):
        self.erasure = 0
        self.E[0].reset()
        self.E[1].reset()


class Edge(object):
    """
    Edge object with parameters:
    type        0 for X, 1 for Z
    vertices    tuple of the two conected vertices
    state       boolean indicating the state of the qubit
    cluster     Cluster object of which this edge is apart of
    peeled      boolean indicating whether this edge has peeled
    matching    boolean indicating whether this edge is apart of the matching
    """

    def __init__(self, qubit, ertype, z=0, edge_type=0):
        # fixed parameters
        self.qubit = qubit
        self.ertype = ertype
        self.z = z
        self.edge_type = edge_type
        if edge_type == 0:
            self.orientation = "-" if self.ertype == self.qubit.qID[0] else "|"
        else:
            self.orientation = "~"

        # iteration parameters
        self.cluster    = None
        self.erasure    = 0
        self.state      = 0
        self.support    = 0
        self.peeled     = 0
        self.matching   = 0

    def __repr__(self):
        errortype = "X" if self.ertype == 0 else "Z"
        return "e{}{}({},{}|{})".format(errortype, self.orientation, *self.qubit.qID[1:], self.z)

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
