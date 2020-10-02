from abc import ABC
from typing import Any, List, Tuple, Union


class Qubit(ABC):
    """General type qubit object

    Parameters
    ----------
    loc : tuple of int of float
        Location of the qubit in (x,y,z) coordinates.
    z : int or float, optional
        Layer position of qubit. Different layers correspond to time instances of a surface for faulty measurement simulations.

    See Also
    --------
    AncillaQubit : Ancilla-qubit class.
    PseudoQubit : Pseudo-qubit class.
    DataQubit : Data-qubit class.

    Notes
    -----
    This class mainly serves as a superclass or template to other more useful qubit types, which have the apprioate subclass attributes and subclass methods. For other types to to the 'See Also' section.
    """

    qubit_type = "qubit"

    def __init__(self, loc: Tuple[float, float], z: float = 0, *args, **kwargs):
        self.loc = loc
        self.z = z

    def __repr__(self):
        return "{}{}|{})".format(self.qubit_type, self.loc, self.z)


class DataQubit(Qubit):
    """Data type qubit object

    Attributes
    ----------
    state : dict of bool
        The state of a DataQubit` is a class property that calls to each of the edges stored at the `edges` attribute and returns all edge states as a dictionary.
    edges : dict of Edge
        Dictionary of Edge objects with the error type as key (e.g. "x" or "z").

    See Also
    --------
    Qubit : Template-qubit class.
    Data_qubit : Data-qubit class.
    Edge : Edge class.
    """

    qubit_type = "data"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.edges = {}

    def reset(self):
        """Resets this qubit's attributes."""
        for edge in self.edges.values():
            edge.reset()

    @property
    def state(self):
        return {key: self.edges[key].state for key in self.edges.keys()}

    @state.setter
    def state(self, new_state: Union[dict, Tuple[bool, bool]]):
        if type(new_state) == dict:
            for key, value in new_state.items():
                if key in self.edges:
                    self.edges[key].state = value
        elif type(new_state) == tuple:
            for edge, state in zip(self.edges.values(), new_state):
                edge.state = state
        else:
            raise TypeError("new_state must be a dictionary or tuple")


class AncillaQubit(Qubit):
    """
    General type qubit object

    Parameters
    ----------
    state_type : str, optional
        Type of edges belonging to the data qubits entangled to the current ancilla qubit for stabilizer measurements (e.g. "x" or "z").

    Attributes
    ----------
    state : bool
        Result of the stabilizer measurement on this ancilla qubit.
    mstate : bool
        Boolean indicating a measurement error on this ancilla qubit.
    parity_qubits : dict of DataQubit
        All data_qubits in this dictionary are entangled to the current ancilla qubit for stabilizer measurements.
    vertical_ancillas : dict of AncillaQubit
        Vertically connected ancilla qubit that is an instance of the same qubit at a different time, required for faulty measurements. Instances at `u` or `up` refer to instances later in time, and instances at `d` or `down` refer to an instances prior in time.

    See Also
    --------
    Qubit : Template-qubit class.
    DataQubit : Data-qubit class.
    Edge : Edge class.

    Examples
    --------
    The state of the entangle DataQubit is located at:

        >>> AncillaQubit.parity_qubits[key].edges[AncillaQubit.state_type]
        True
    """

    qubit_type = "ancilla"

    def __init__(self, *args, state_type: str = "default", **kwargs):
        super().__init__(*args, **kwargs)
        self.state_type = state_type
        self.parity_qubits = {}
        self.vertical_ancillas = {}
        self.vertical_edges = {}
        self.mstate = False
        self.state = False


class Edge(object):
    """An edge object belonging to a qubit

    Parameters
    ----------
    qubit : Qubit
        Parent qubit object.
    state_type : str, optional
        Error type associated with the current edge.
    rep : str, optional
        Short string used in the object represenation.

    Attributes
    ----------
    nodes : list of AncillaQubit
        Two AncillaQubit-like objects that are the nodes of the edge.
    state : bool
        The current quantum state on the edge object.

    See Also
    --------
    AncillaQubit : Ancilla-qubit class.
    """

    edge_type, rep = "edge", "-"

    def __init__(
        self,
        qubit,
        state_type: str = "",
    ):
        # fixed parameters
        self.qubit = qubit
        self.state_type = state_type
        self._nodes = []
        self.state = False

    def __call__(self):
        return self.state

    def __repr__(self):
        return "e{}{}{}|{}".format(self.state_type, self.rep, self.qubit.loc, self.qubit.z)

    @property
    def nodes(self):
        return self._nodes

    @nodes.setter
    def nodes(self, nodes: Tuple[AncillaQubit, AncillaQubit]):
        self._nodes = nodes

    def add_node(self, node: AncillaQubit, **kwargs):
        """Adds a node to the edge's `nodes` attribute."""
        if len(self._nodes) < 2:
            self._nodes.append(node)
            if len(self._nodes) == 2:
                self._nodes == tuple(self._nodes)
        else:
            raise ValueError("This edge already has two nodes.")


class PseudoQubit(AncillaQubit):
    """Boundary element, imitates AncillaQubit.

    Edges needs to be spanned by two nodes. For data qubits on the boundary, one of its edges additionaly requires an ancilla qubit like node, which is the PseudoQubit.
    """

    qubity_type = "pseudo"


class PseudoEdge(Edge):
    """Vertical edge connecting time instances of AncillaQubits, imitates Edge."""

    edge_type, rep = "pseudo", "|"
