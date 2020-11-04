from abc import ABC
import random
from typing import Optional, Tuple, Union
from collections import defaultdict


class Qubit(ABC):
    """General type qubit object.

    # This class mainly serves as a superclass or template to other more useful qubit types, which have the apprioate subclass attributes and subclass methods. For other types to to the 'See Also' section.

    Parameters
    ----------
    loc
        Location of the qubit in coordinates.
    z
        Layer position of qubit. Different layers correspond to time instances of a surface for faulty measurement simulations.
    """

    qubit_type = "Q"

    def __init__(self, loc: Tuple[float, float], z: float = 0, *args, **kwargs):
        self.loc = loc
        self.z = z
        self.errors = defaultdict(float)

    def __repr__(self):
        return f"{self.qubit_type}({self.loc[0]},{self.loc[1]}|{self.z})"


class DataQubit(Qubit):
    """Data type qubit object.

    The state of a data-qubit is determined by two `~.codes.elements.Edge` objects stored in the ``self.edges`` dictionary. Each of the edges are part of a separate graph on the surface lattice.


    Attributes
    ----------
    edges : dict of `~.codes.elements.Edge`
        Dictionary of edges with the error type as key (e.g. ``"x"`` or ``"z"``).

            self.edges = {"x": Edge_x, "z", Edge_z}

    state : dict of bool
        A class property that calls to each of the edges stored at the `self.edges` attribute and returns all edge states as a dictionary.

    reinitialized : bool
        Indicator for a reinitialized (replaced) data qubit.
    """

    qubit_type = "D"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.edges = {}
        self.reinitialized = True

    def _reinitialize(self, initial_states: Tuple[float, float] = (None, None), **kwargs):
        """Resets this qubit's attributes."""
        self.reinitialized = True
        for edge, state in zip(self.edges.values(), initial_states):
            edge._reinitialize(initial_state=state, **kwargs)

    @property
    def state(self):
        self.reinitialized = False
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
    General type qubit object.

    An ancilla-qubit is entangled to one or more `~codes.elements.DataQubit` objects. The ``self.state_type`` attribute determines the state on which the measurement is applied. A single measurement is applied when the class property ``self.state`` is called. The state of the last measurement is stored in ``self.measured_state`` for state access without prompting a new measurement.

    Parameters
    ----------
    state_type : str, {"x", "z"}
        Type of 'codes.elements.Edge' objects belonging to the `~.codes.elements.DataQubit` objects entangled to the current ancilla-qubit for stabilizer measurements.

    Attributes
    ----------
    parity_qubits : dict of `~.codes.elements.DataQubit`
        All qubits in this dictionary are entangled to the current ancilla for stabilizer measurements.
    z_neighbors : {`.codes.elements.AncillaQubit`: `~.codes.elements.PseudoEdge`}
        Neighbor ancilla in the z direction that is an instance of the same qubit at a different time, required for faulty measurements.
    state : bool
        Property that measures the parity of the qubits in ``self.parity_qubits``.
    measured_state : bool
        The result of the last parity measurement.
    syndrome : bool
        Whether the current ancilla is a syndrome.
    measurement_error : bool
        Whether an error occurred during the last measurement.

    Examples
    --------
    The state of the entangled `~.codes.elements.DataQubit` is located at:

        >>> AncillaQubit.parity_qubits[key].edges[AncillaQubit.state_type]
        True
    """

    qubit_type = "A"

    def __init__(self, *args, state_type: str = "default", **kwargs):
        super().__init__(*args, **kwargs)
        self.state_type = state_type
        self.measured_state = False
        self.syndrome = False
        self.parity_qubits = {}
        self.z_neighbors = {}
        self.measurement_error = False

    @property
    def state(self):
        return self.measure()

    def measure(self, p_bitflip_plaq: float = 0, p_bitflip_star: float = 0, **kwargs) -> bool:
        """Applies a parity measurement on the ancilla.

        The functions loops over all the data qubits in ``self.parity_qubits``. For every edge associated with the entangled state on the data qubit, the value of a ``parity`` boolean is flipped.

        Parameters
        ----------
        p_bitflip_plaq : float
            Bitflip rate for plaquette (XXXX) operators.
        p_bitflip_star : float
            Bitflip rate for star (ZZZZ) operators.
        """
        parity = False
        for data_qubit in self.parity_qubits.values():
            if data_qubit.state[self.state_type]:
                parity = not parity

        p_measure = p_bitflip_plaq if self.state_type == "x" else p_bitflip_star
        self.measurement_error = p_measure != 0 and random.random() < p_measure
        if self.measurement_error:
            parity = not parity

        self.measured_state = parity
        self.syndrome = parity

        return parity


class Edge(object):
    """A state object belonging to a `~.codes.elements.DataQubit` object.

    An edge cannot have open vertices and must be spanned by two nodes. In this case, the two nodes must be `~.codes.elements.AncillaQubit` objects, and are stored in ``self.nodes``.

    Parameters
    ----------
    qubit
        Parent qubit object.
    state_type
        Error type associated with the current edge.
    initial_state
        State of the object after initialization.

    Attributes
    ----------
    nodes : list of two ~.codes.elements.AncillaQubit` objects
        The vertices that spans the edge.
    state : bool
        The current quantum state on the edge object.
    """

    edge_type, rep = "edge", "-"

    def __init__(
        self,
        qubit: DataQubit,
        state_type: str = "",
        initial_state: Optional[bool] = None,
        **kwargs,
    ):
        # fixed parameters
        self.qubit = qubit
        self.state_type = state_type
        self._nodes = []
        self.state = random.random() > 0.5 if initial_state is None else initial_state

    def _reinitialize(self, initial_state: Optional[bool] = None, **kwargs):
        self.state = random.random() > 0.5 if initial_state is None else initial_state

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
        """Adds a node to the edge's ``self.nodes`` attribute."""
        if len(self._nodes) < 2:
            self._nodes.append(node)
            if len(self._nodes) == 2:
                self._nodes == tuple(self._nodes)
        else:
            raise ValueError("This edge already has two nodes: {}".format(self._nodes))


class PseudoQubit(AncillaQubit):
    """Boundary element, imitates `.codes.elements.AncillaQubit`.

    Edges needs to be spanned by two nodes. For data qubits on the boundary, one of its edges additionally requires an ancilla qubit like node, which is the pseudo-qubit.
    """

    qubit_type = "pA"


class PseudoEdge(Edge):
    """Vertical edge connecting time instances of ancilla-qubits, imitates `.codes.elements.Edge`."""

    edge_type, rep = "pseudo", "|"
