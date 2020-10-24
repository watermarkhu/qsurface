from abc import ABC
import random
from typing import Tuple, Union


class Qubit(ABC):
    """General type qubit object.

    This class mainly serves as a superclass or template to other more useful qubit types, which have the apprioate subclass attributes and subclass methods. For other types to to the 'See Also' section.

    Parameters
    ----------
    loc : tuple, (x,y)
        Location of the qubit in coordinates.
    z : int or float, optional
        Layer position of qubit. Different layers correspond to time instances of a surface for faulty measurement simulations.
    """

    qubit_type = "Q"

    def __init__(self, loc: Tuple[float, float], z: float = 0, *args, **kwargs):
        self.loc = loc
        self.z = z

    def __repr__(self):
        return f"{self.qubit_type}{self.loc}|{self.z})"


class DataQubit(Qubit):
    """Data type qubit object.

    The state of a data-qubit is determined by two `~opensurfacesim.codes._template.Edge` objects stored in the `self.edges` dictionary. Each of the edges are part of a separate graph on the surface lattice.


    Attributes
    ----------
    edges : dict of `.Edge`
        Dictionary of edges with the error type as key (e.g. ``"x"`` or ``"z"``).

            self.edges = {"x": Edge_x, "z", Edge_z}

    state : dict of bool
        A class property that calls to each of the edges stored at the `self.edges` attribute and returns all edge states as a dictionary.
    """

    qubit_type = "D"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.edges = {}

    def _reset(self):
        """Resets this qubit's attributes."""
        for edge in self.edges.values():
            edge._reset()

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

    def state_icon(self):
        """Returns the qubit state in a colored icon."""
        if self.state["x"] and self.state["z"]:
            return "🟡"
        elif self.state["x"]:
            return "🔴"
        elif self.state["z"]:
            return "🟢"
        else:
            return "⚪"


class AncillaQubit(Qubit):
    """
    General type qubit object.

    An ancilla-qubit is entangled to one or more `~opensurfacesim.codes._template.DataQubit` objects. The `self.state_type` attribute determines the state on which the measurement is applied. A single measurement is applied when the class property `self.state` is called. The state of the last measurement is stored in `self.measured_state` for state access without prompting a new measurement.

    Parameters
    ----------
    state_type : str, {"x", "z"}
        Type of '.Edge' objects belonging to the '~opensurfacesim.codes._template.DataQubit` objects entangled to the current ancilla-qubit for stabilizer measurements.

    Attributes
    ----------
    parity_qubits : dict of `~opensurfacesim.codes._template.DataQubit`
        All qubits in this dictionary are entangled to the current ancilla for stabilizer measurements.
    vertical_ancillas : dict of `~opensurfacesim.codes._template.AncillaQubit`
        Vertically connected ancilla that is an instance of the same qubit at a different time, required for faulty measurements. Instances at *u* or *up* refer to instances later in time, and instances at *d* or *down* refer to an instances prior in time.
    state : bool
        Property that measures the parity of the qubits in `self.parity_qubits`.
    measured_state : bool
        The result of the last parity measurement.
    syndrome : bool
        Whether the current ancilla is a syndrome.
    measurement_error : bool
        Whether an error occurred during the last measurement.

    Examples
    --------
    The state of the entangled `~opensurfacesim.codes._template.DataQubit` is located at:

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
        self.vertical_ancillas = {}
        self.measurement_error = False

    @property
    def state(self):
        return self.get_state(0)

    def get_state(self, pm_bitflip: float = 0, pm_phaseflip: float = 0, **kwargs) -> bool:
        """Applies a parity measurement on the ancilla with probability ``p_bitflip``.

        The functions loops over all the data qubits in ``self.parity_qubits``. For every edge associated with the entangled state on the data qubit, the value of a ``parity`` boolean is flipped.

        Parameters
        ----------
        p_bitflip : float
            Bitflip probability. 
        """
        parity = False
        for data_qubit in self.parity_qubits.values():
            edge = data_qubit.edges[self.state_type]
            if edge.state:
                parity = not parity

        p_measure = pm_bitflip if self.state_type == "x" else pm_phaseflip
        self.measurement_error = p_measure != 0 and random.random() < p_measure
        if self.measurement_error:
            parity = not parity

        self.measured_state = parity
        self.syndrome = parity

        return parity

    def state_icon(self):
        """Returns the qubit state in a colored icon."""
        if self.state_type == "x":
            return "🟧" if self.state else "🟦"
        else:
            return "🔶" if self.state else "🔷"


class Edge(object):
    """A state object belonging to a `~opensurfacesim.codes._template.DataQubit` object.

    An edge cannot have open vertices and must be spanned by two nodes. In this case, the two nodes must be `~opensurfacesim.codes._template.AncillaQubit` objects, and are stored in ``self.nodes``.

    Parameters
    ----------
    qubit : `~opensurfacesim.codes._template.DataQubit`
        Parent qubit object.
    state_type : str,  {"x", "z"}
        Error type associated with the current edge.

    Attributes
    ----------
    nodes : list of two ~opensurfacesim.codes._template.AncillaQubit` objects
        The vertices that spans the edge.
    state : bool
        The current quantum state on the edge object.
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

    def _reset(self):
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
        """Adds a node to the edge's ``self.nodes`` attribute."""
        if len(self._nodes) < 2:
            self._nodes.append(node)
            if len(self._nodes) == 2:
                self._nodes == tuple(self._nodes)
        else:
            raise ValueError("This edge already has two nodes: {}".format(self._nodes))


class PseudoQubit(AncillaQubit):
    """Boundary element, imitates `.AncillaQubit`.

    Edges needs to be spanned by two nodes. For data qubits on the boundary, one of its edges additionally requires an ancilla qubit like node, which is the pseudo-qubit.
    """
    
    qubit_type = "pA"


class PseudoEdge(Edge):
    """Vertical edge connecting time instances of ancilla-qubits, imitates `.Edge`."""

    edge_type, rep = "pseudo", "|"
