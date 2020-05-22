'''
2020 Mark Shui Hu, QuTech

www.github.com/watermarkhu/oop_surface_code
_____________________________________________

We define the unit cell, which contains two qubits, a star operator and plaquette operator.

    |       |
- Star  -  Q_0 -     also top (T) qubit
    |       |
-  Q_1  - Plaq  -    also down (D) qubit
    |       |

Each cell is indicated by its y and x coordiantes. As such every qubit and stabilizer can by identified by a unique ID number:

Qubits: qID (td, y, x)          Stabilizers: sID (ertype, y, x)
    Q_0:    (0, y, x)               Star:   (0, y, x)
    Q_1:    (1, y, x)               Plaq:   (1, y, x)

The 2D graph (toric/planar) is a square lattice with 1 layer of these unit cells.
'''
from ..plot import plot_graph_lattice as pgl
from ..plot import plot_unionfind as puf
import random


class toric(object):
    """
    The graph in which the vertices, edges and clusters exist. Has the following parameters

    size            1D size of the graph
    range           range over 1D that is often used
    decoder         decoder object to use for this graph, also saves graph object to decoder object
    decode_layer    z layer on which the qubits is decoded, 0 for 2D graph graph
    C               dict of clusters with
                        Key:    cID number
                        Value:  Cluster object
    S               dict of stabilizers with
                        Key:    sID number
                        Value:  Stab object
    Q               dict of qubits with
                        Key:    qID number
                        Value:  Qubit object with two Edge objects
    matching_weight total length of edges in the matching
    """
    def __init__(self, size, decoder, *args, plot_config={}, dim=2, **kwargs):
        self.dim = dim
        self.size = size
        self.range = range(size)
        self.decoder = decoder
        decoder.graph = self
        self.decode_layer = 0
        self.cID = 0
        self.C, self.S, self.Q = {}, {}, {}
        self.matching_weight = []

        self.init_graph_layer()

        for key, value in kwargs.items():
            setattr(self, key, value)
        self.plot_config = plot_config
        self.gl_plot = pgl.plot_2D(self, **plot_config) if self.plot2D else None


    def __repr__(self):
        return f"2D {self.__class__.__name__} graph object with"

    def init_uf_plot(self):
        '''
        Initializes plot of unionfind decoder.
        '''
        self.uf_plot = puf.plot_2D(self, **self.plot_config)
        return self.uf_plot


    def count_matching_weight(self, z=0):
        '''
        Loops through all qubits on the layer and counts the number of matchings edges
        '''
        weight = 0
        for qubit in self.Q[z].values():
            if qubit.E[0].matching == 1:
                weight += 1
            if qubit.E[1].matching == 1:
                weight += 1
        self.matching_weight.append(weight)
    '''
    ########################################################################################

                                    Surface code functions

    ########################################################################################
    '''

    def init_graph_layer(self, z=0):
        '''
        param z     layer
        Initializes a layer of the graph structure of a toric lattice
        '''
        self.dirs = ["n", "s", "e", "w"]
        self.S[z], self.Q[z], = {}, {}

        # Add stab objects to graph
        for ertype in [0,1]:
            for y in self.range:
                for x in self.range:
                    self.add_stab(ertype, y, x, z)

        # Add edges to graph
        for y in self.range:
            for x in self.range:
                vW, vE = self.S[z][(0, y, x)], self.S[z][(0, y, (x + 1) % self.size)]
                vN, vS = self.S[z][(1, (y - 1) % self.size, x)], self.S[z][(1, y, x)]
                self.add_qubit(0, y, x, z, vW, vE, vN, vS)

                vN, vS = self.S[z][(0, y, x)], self.S[z][(0, (y + 1) % self.size, x)]
                vW, vE = self.S[z][(1, y, (x - 1) % self.size)], self.S[z][(1, y, x)]
                self.add_qubit(1, y, x, z, vW, vE, vN, vS)


    def apply_and_measure_errors(self, pX=0, pZ=0, pE=0, **kwargs):
        '''
        Initilizes errors on the qubits and measures the stabilizers on the graph
        '''

        self.init_erasure(pE=pE)
        self.init_pauli(pX=pX, pZ=pZ)         # initialize errors
        self.measure_stab()                       # Measure stabiliziers


    def init_erasure(self, pE=0, **kwargs):
        """
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
        The measurement outcomes of the stabilizers, which are the vertices on the self are saved to their corresponding vertex objects.
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
    '''
    Inherits all the class variables and methods of the graph_2D.toric object.
    Additions:
        params:
            B   dict of boundary objects with
                    Key:    sID number
                    Value:  Stab object

    Replaces:
        methods:
            init_graph_layer()
            logical_error()
            reset()
    '''
    def __init__(self, *args, **kwargs):
        self.B = {}
        super().__init__(*args, **kwargs)

    def init_graph_layer(self, z=0):
        '''
        param z     layer
        Initializes a layer of the graph structure of a planar lattice
        '''
        self.dirs = ["n", "s", "e", "w"]
        self.S[z], self.Q[z], self.B[z]= {}, {}, {}

        # Add vertices and boundaries to graph
        for yx in self.range:
            for xy in range(self.size - 1):
                self.add_stab(0, yx, xy + 1, z)
                self.add_stab(1, xy, yx, z)

            self.add_boundary(0, yx, 0, z)
            self.add_boundary(0, yx, self.size, z)
            self.add_boundary(1, -1, yx, z)
            self.add_boundary(1, self.size - 1, yx, z)

        # Add edges to graph
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
        """
        Finds whether there are any logical errors on the lattice/self. The logical error is returned as [Xhorizontal, Zvertical], where each item represents a homological Loop
        """

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
        """
        Resets the graph by resetting all boudaries and interited objects
        """
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
    boundary    len(2) list containing 1) current boundary, 2) next boundary
    bucket      the appropiate bucket number of this cluster
    support     growth state of the cluster: 1 if False, 2 if True

    [planar]
    on_bound    whether this clusters is connected to the boundary

    [evengrow]
    root_node   the root node of the anyontree representing this cluster
    calc_delay  list of nodes in this anyontree for which it and its children has undefined delays
    self.mindl  the minimal delay value of anyonnodes in this anyontree/cluster, which can be <1
    """
    def __init__(self, cID, vertex):
        # self.inf = {"cID": cID, "size": 0, "parity": 0}
        self.cID        = cID
        self.size       = 0
        self.parity     = 0
        self.parent     = self
        self.childs     = [[], []]
        self.boundary   = [[], []]
        self.bucket     = 0
        self.support    = 0
        self.on_bound   = 0
        self.root_node  = vertex.node
        self.calc_delay = []
        self.mindl      = 0
        self.add_vertex(vertex)

    def __repr__(self):
        return "C" + str(self.cID) + "(" + str(self.size) + ":" + str(self.parity) + ")"

    def __hash__(self):
        return self.cID

    def add_vertex(self, vertex):
        """Adds a stabilizer to a cluster. Also update cluster value of this stabilizer."""
        self.size += 1
        if vertex.state:
            self.parity += 1
        vertex.cluster = self


class Stab(object):
    """
    Object that are both:
        - the stabilizers on the toric/planar lattice
        - the vertices on the uf-lattice

    [fixed parameters]
    type        0 for stab object, 1 for boundary (inherited)
    sID         location of stabilizer (ertype, y, x)
    z           layer of graph to which this stab belongs
    neighbors   dict of the neighobrs (in the graph) of this stabilizer with
                    Key:    direction
                    Value   (Stab object, Edge object)

    [iteration parameters]
    parity      boolean indicating the outcome of the parity measurement on this stab
    state       boolean indicating anyon state of stabilizer
    mstate      boolean indicating measurement error on this stab (for plotting)
    cluster     Cluster object of which this stabilizer is apart of
    tree        boolean indicating whether this stabilizer has been traversed

    [iteration parameters: evengrow]
    node        the anyonnode in which this stab/uf-lattice-vertex is rooted
    new_bound   temporary storage list for new boundary of a cluster

    """
    def __init__(self, sID, type=0, z=0):
        self.type       = type
        self.sID        = sID
        self.z          = z
        self.neighbors  = {}
        self.parity     = 0
        self.state      = 0
        self.mstate     = 0
        self.cluster    = None
        self.forest     = 0
        self.tree       = 0
        self.node       = None
        self.new_bound  = []

    def __repr__(self):
        type = "X" if self.sID[0] == 0 else "Z"
        return "v{}({},{}|{})".format(type, *self.sID[1:], self.z)

    def picker(self):
        cluster = self.cluster.parent if self.cluster else None
        if self.node:
            return "{}-{}-{}".format(self.__repr__(), self.node.tree_rep(), cluster)
        else:
            return "{}-{}".format(self.__repr__(), cluster)


    def reset(self):
        """
        Changes all iteration paramters to their initial value
        """
        self.state      = 0
        self.mstate     = 0
        self.parity     = 0
        self.cluster    = None
        self.forest     = 0
        self.tree       = 0
        self.node       = None


class Bound(Stab):
    '''
    Object that are both:
        - the boundaries on the toric/planar lattice
        - the vertices on the uf-lattice

    Iherits all class variables and methods of Stab object
    '''
    def __init__(self, sID, z=0):
        super().__init__(sID, type=1, z=z)

    def __repr__(self):
        type = "X" if self.sID[0] == 0 else "Z"
        return "b{}({},{}|{})".format(type, *self.sID[1:], self.z)


class Qubit(object):
    '''
    Qubit object representing the physical qubits on the lattice.

    [fixed parameters]
    qID         (td, y, x)
    z           layer of graph to which this stab belongs
    E           list countaining the two edges of the primal and secundary lattice

    [iteration parameters]
    erasure     boolean of erased qubit
    '''
    def __init__(self, qID, z=0):
        self.qID        = qID
        self.z          = z
        self.E          = [Edge(self, ertype=0, z=z), Edge(self, ertype=1, z=z)]
        self.erasure    = 0

    def __repr__(self):
        return "q({},{}:{}|{})".format(*self.qID[1:], self.qID[0], self.z)

    def picker(self):
        return self.__repr__()

    def reset(self):
        """
        Changes all iteration parameters to their default value
        """
        self.E[0].reset()
        self.E[1].reset()
        self.erasure = 0



class Edge(object):
    """
    Edges on the uf-lattice, of which each qubit on the surface lattice has two.

    [fixed parameters]
    edge_type       0 for horizontal edge (within layer, 2D), 1 for vertical edge (between layers, 3D)
    qubit           qubit object this edge belongs to
    z               layer of graph to which this stab belongs
    ertype          0 for primal lattice connecting X-type vertices,
                    1 for secundary lattice connecting Z-type vertices

    [iteration parameters]
    cluster         Cluster object of which this edge is apart of
    state           boolean indicating the state of the qubit
    support         0 for ungrown, 1 for half-edge, 2 for full-edge
    peeled          boolean indicating whether this edge has peeled
    matching        boolean indicating whether this edge is apart of the matching
    """
    def __init__(self, qubit, ertype, z=0, edge_type=0):
        # fixed parameters
        self.edge_type  = edge_type
        self.qubit      = qubit
        self.ertype     = ertype
        self.z          = z
        self.state      = 0
        self.support    = 0
        self.peeled     = 0
        self.matching   = 0
        self.forest     = 0


    def __repr__(self):
        if self.edge_type == 0:
            orientation = "-" if self.ertype == self.qubit.qID[0] else "|"
        else:
            orientation = "~"
        errortype = "X" if self.ertype == 0 else "Z"
        return "e{}{}({},{}|{})".format(errortype, orientation, *self.qubit.qID[1:], self.z)

    def picker(self):
        return "{}-{}".format(self.__repr__(), self.qubit)

    def reset(self):
        """
        Changes all iteration paramters to their initial value
        """
        self.state      = 0
        self.support    = 0
        self.peeled     = 0
        self.matching   = 0
        self.forest     = 0
