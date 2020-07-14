#%%
class Qubit(object):
    """
    General type qubit object

    Parameters
    ----------
    loc : tuple or list of length 3
        Location of the qubit in (x,y,z) coordinates.
    Type : str, optional
        Name of the current qubit time. Short names withough spaces are preferred (the default is 'Qubit')


    See Also
    --------
    Ancilla_qubit
    Data_qubit


    Notes
    -----
    This class mainly serves as a superclass or template to other more useful qubit types, which have the apprioate subclass attributes and subclass methods. For other types to to the 'See Also' section. 
    """
    def __init__(self, loc=(0,0,0), Type="Qubit", *args, **kwargs):
        self.Type = Type
        self.loc = loc

    def __repr__(self):
        return "{}({},{}|{})".format(self.Type, *self.loc)

    def picker(self):
        """Returns selftext for pick action during plotting. 
        """
        return self.__repr__()



class Data_qubit(Qubit):
    """
    Data type qubit object

    Parameters
    ----------
    loc : tuple or list of length 3
        Location of the qubit in (x,y,z) coordinates.
    Type : str, optional
        Name of the current qubit time. Short names withough spaces are preferred (the default is 'Qubit')


    Attributes
    ----------
    state 
    edges : dict
        Dictionary of `Edge` objects with the error type as key (e.g. `"X"` or `"Z"`). 


    See Also
    --------
    Qubit
    Data_qubit
    Boundary
    Edge
    """
    def __init__(self, *args, Type="data", **kwargs):
        super().__init__(*args, Type=Type, **kwargs)
        self.edges = dict()

    def reset(self):
        """Resets this qubit's attributes.
        """
        self.state = False
        super().reset()
        for edge in self.edges.values():
            edge.reset()

    @property
    def state(self):
        """Current state of the `Data_qubit`. 
        
        The state of a `Data_qubit` is a class property that calls to each of the edges stored at the `edges` attribute and returns all edge states as a dictionary. 
        """
        return {key: self.edges[key].state for key in self.edges.keys()}

    @state.setter
    def state(self, new_state):
        if type(new_state) == dict:
            for key, value in new_state.items():
                if key in self.edges:
                    self.edges[key].state = value
        else:
            raise TypeError("new_state must be a dictionary")


class Ancilla_qubit(Qubit):
    """
    General type qubit object

    Parameters
    ----------
    loc : tuple or list of length 3
        Location of the qubit in (x,y,z) coordinates.
    EdgeType : str, optional
        Type of edges belonging to the data qubits entangled to the current ancilla qubit for stabilizer measurements.
    Type : str, optional
        Name of the current qubit time. Short names withough spaces are preferred (the default is 'Qubit').


    Attributes
    ----------
    state : bool
        Result of the stabilizer measurement on this ancilla qubit. 
    mstate : bool
        Boolean indicating a measurement error on this ancilla qubit.
    parity_qubits : dict of `Data_qubit` 
        All data_qubits in this dictionary are entangled to the current ancilla qubit for stabilizer measurements. The entangled state is located at `Data_qubit.edges[Ancilla_qubit.EdgeType]`.
    vertical_ancillas : dict of 'Ancilla_qubit`
        Vertically connected ancilla qubit that is an instance of the same qubit at a different time. Vertical elements are needed when `graph.faulty_measurements` is the graph class. Instances at `u` or `up` refer to instances later in time, and instances at `d` or `down` refer to an instances prior in time.


    See Also
    --------
    Qubit
    Data_qubit
    Edge
    """

    def __init__(self, *args, EdgeType='default', Type="ancilla", **kwargs):
        super().__init__(*args, Type=Type, **kwargs)
        self.EdgeType = EdgeType
        self.parity_qubits = {}
        self.vertical_ancillas = {}
        self.vertical_edges = {}
        self.init_state()

    def init_state(self):
        """(Re)initializes the `Data_qubit` subclass attributes.
        """
        self.mstate = False
        self.state = False

    def reset(self):
        """Resets this qubit's attributes.
        """
        self.state = False
        super().reset()
        self.init_state()


def pair_entangle(ancillaQ, dataQ, key, edge=None, **kwargs):
    """Entangles one `data_qubit` to the current ancilla qubit

    Parameters
    ----------
    key : str or int
        Key for the `data_qubit` in the `parity_qubits` dictionary
    data_qubit : Data_qubit
        Qubit to entangle.
    edge : Edge, optional
        The `Edge` object related to the state of the `Data_qubit` to entangle to.
    """
    ancillaQ.parity_qubits[key] = dataQ
    if edge is None:
        edge = dataQ.edges[ancillaQ.EdgeType]
    edge.nodes += [ancillaQ]


def pair_time(newAQ, oldAQ, edge, **kwargs):
    """Pair another instance of the current ancilla at 1 time unit prior or later.

    Parameters
    ----------
    newAQ : Ancilla_qubit
        Instance of the ancilla at time `t+1`.
    oldAQ : Ancilla_qubit
        Instance of the ancilla at time `t`.
    edge : Edge
        Edge object connecting the two instances

    """
    newAQ.vertical_ancillas["d"] = oldAQ
    oldAQ.vertical_ancillas["u"] = newAQ
    newAQ.vertical_edges["d"] = edge
    oldAQ.vertical_edges["u"] = edge
    edge.nodes += [newAQ, oldAQ]



def measure_parity(ancillaQ, **kwargs):
    """Applies a parity measurement on the ancilla.

    The functions loops over all the data qubits in the `parity_qubits` attribute of `ancillaQ`. For every edge associated with the entangled state on the data qubit, the value of a `parity` boolean is flipped. 

    Parameters
    ----------
    ancillaQ : Ancilla_qubit
        The ancilla to apply the parity measurement on.

    
    Returns
    -------
    parity : bool
        Result of the parity measurment.
    """
    parity = False
    for qubit in ancillaQ.parity_qubits.values():
        edge = qubit.edges[ancillaQ.EdgeType]
        if edge.state:
            parity = not parity
    ancillaQ.state = parity
    return parity


class Boundary(Ancilla_qubit):
    """Boundary element
    
    Edges needs to be spanned by two nodes. For data qubits on the boudnary, one of its edges additionaly requires an ancilla qubit like node, which is the boundary element. 
    """
    def __init__(self, Type="bound", *args, **kwargs):
        super().__init__(*args, Type=Type, **kwargs)


class Edge(object):
    """A quantum edge object belonging to a qubit

    Parameters
    ----------

    qubit : Qubit
        Parent qubit object.
    Type : str, optional
        Error type associated with the current quantum edge.
    rep : str, optional
        Short string used in the object represenation.

    Attributes
    ----------
    nodes
    state : bool
        The current quantum state on the edge object.
    matching : bool
        Indicator for whether the edge is part of the matching.
    """

    def __init__(self, qubit, Type="default", rep="-"):
        # fixed parameters
        self.qubit = qubit
        self.Type=Type
        self.rep = rep
        self._nodes = []
        self.reset()
    
    def reset(self):
        self.state = False
        self.matching = False
    
    def __call__(self):
        return self.state

    def __repr__(self):
        return "e{}{}({},{}|{})".format(self.Type, self.rep, *self.qubit.loc)

    @property
    def nodes(self):
        """List of two `Ancilla_qubit` like object that act as the nodes of the edge. 
        """
        return self._nodes

    @nodes.setter
    def nodes(self, items):
        if len(items) > 2:
            raise IndexError("Edge component can only have two connected nodes")
        self._nodes = items

    def picker(self):
        """Returns selftext for pick action during plotting. 
        """
        return self.__repr__()


