#%%
class Qubit(object):
    def __init__(self, loc=(0,0,0), Type="Qubit", *args, **kwargs):
        self.Type = Type
        self.loc = loc
        self.state = 0

    def __repr__(self):
        return "{}({},{}|{})".format(self.Type, *self.loc)

    def picker(self):
        return self.__repr__()

    def reset(self):
        self.state = 0


class Ancilla_qubit(Qubit):
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
    """

    def __init__(self, *args, EID=0, Type="ancilla", **kwargs):
        super().__init__(*args, Type=Type, **kwargs)
        self.EID = EID
        self.parity_qubits = {}
        self.mstate = 0

    def add_parity_qubit(self, key, parity_qubit):
        self.parity_qubits[key] = (parity_qubit, self.EID)
        parity_qubit.E[self.EID].new_node(self)

    def measure_parity(self, **kwargs):
        parity = 0
        for qubit, EID in self.parity_qubits.values():
            if qubit.E[EID].state:
                parity = 1 - parity
        self.state = parity
        return parity

    def reset(self):
        super().reset()
        self.mstate = 0


class Boundary(Ancilla_qubit):
    '''
    Object that are both:
        - the boundaries on the toric/planar lattice
        - the vertices on the uf-lattice

    Iherits all class variables and methods of Stab object
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, Type="bound", **kwargs)


class Data_qubit(Qubit):
    '''
    Qubit object representing the physical qubits on the lattice.

    [fixed parameters]
    qID         (td, y, x)
    z           layer of graph to which this stab belongs
    E           list countaining the two edges of the primal and secundary lattice

    [iteration parameters]
    erasure     boolean of erased qubit
    '''

    def __init__(self, *args, Type="data", **kwargs):
        super().__init__(*args, Type=Type, **kwargs)
        self.E = [Edge(self, ID=0), Edge(self, ID=1)]

    @property
    def state(self):
        return [self.E[0].state, self.E[1].state]

    @state.setter
    def state(self, new_state):
        if type(new_state) == list and len(new_state) == 2:
            self.E[0].state = new_state[0]
            self.E[1].state = new_state[1]

    def reset(self):
        super().reset()
        self.E[0].reset()
        self.E[1].reset()


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

    def __init__(self, qubit, ID, edge_type=0):
        # fixed parameters
        self.qubit = qubit
        self.edge_type = edge_type
        self.ID = ID
        self._nodes = []
        self.state = 0
        self.matching = 0

    def __repr__(self):
        orientation = "-" if self.edge_type == 0 else "|"
        errortype = "X" if self.ID == 0 else "Z"
        return "e{}{}({},{}|{})".format(errortype, orientation, *self.qubit.loc)

    @property
    def nodes(self):
        return self._nodes

    @nodes.setter
    def nodes(self, items):
        if len(items) > 2:
            raise IndexError("Edge component can only have two connected nodes")
        self._nodes = items

    def new_node(self, node):
        new_nodes = self.nodes + [node]
        self.nodes = new_nodes

    def picker(self):
        return self.__repr__()

    def reset(self):
        """
        Changes all iteration paramters to their initial value
        """
        self.state = 0
        self.matching = 0


# %%
