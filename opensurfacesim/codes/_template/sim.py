from abc import ABC, abstractmethod
from .elements import DataQubit, AncillaQubit, PseudoQubit, Edge, PseudoEdge, Qubit
from ...info.benchmark import BenchMarker
from ...errors._template import Error
from typing import List, Optional, Union, Tuple
import importlib
import random


class PerfectMeasurements(ABC):
    """Simulation template code class for perfect measurements.

    Parameters
    ----------
    size : int, tuple
        Size of the surface code in single dimension or two dimensions (y,x).
    dual : bool, optional
        Enables the dual graph. Turn off when only simulating for bit-flip errors.
    benchmarker : Benchmarker, optional
        Benchmarker class. If a benchmarker class is attached, the benchmarker will start to collect the number of calls of to the code class and decoder class methods.

    Attributes
    ----------
    ancilla_qubits : dict of dict of AncillaQubit
        See notes.
    data_qubits: dict of dict of DataQubit
        See notes.
    pseudo_qubits: dict of dict of PseudoQubit
        See notes.
    errors : dict of Error
        Dictionary of error modules with the module name as key. All error modules loaded in `errors` will be applied during a simulation by `apply_errors`.
    logical_operators : dict of list of Edge
        Dictionary with lists of Edges that from a trivial loop over the surface and correspond to a logical operator. The logical state of each operator can be obtained by the state of each Edge in the list.
    logical_state : dict of bool
        Dictionary with the states corresponding to the logical operators in `logical_operators`.
    no_error : bool
        Indicator for whether there is a logical error in the last iteration. The value for `no_error` is updated after a call to `logical_state`.

    See Also
    --------
    opensurfacesim.code._template.elements.DataQubit : Data-qubit class.
    opensurfacesim.code._template.elements.AncillaQubit : Ancilla-qubit class.
    opensurfacesim.code._template.elements.PseudoQubit : Pseudo-qubit class.
    opensurfacesim.code._template.elements.Edge : Edge class.
    opensurfacesim.error : Error modules.
    opensurfacesim.info.benchmark.BenchMarker : Benchmarking class.

    Notes
    -----
    The qubits of the code class are stored in a double dictionary, with the keys in the outer dictionary corresponding to the qubit layer. For perfect measurements, there is a single layer. For faulty measurements, there are multiple layers (and defaults to `size`). In the nested dictionaries each qubit is stored by its `loc` as key. A qubit can thus be accesed by `self.qubits[layer][(x,y)]`.

    The qubit and edge classes from the `elements` module can be replaced with inherited classes to store decoder dependent attributes.
    """

    dataQubit = DataQubit
    ancillaQubit = AncillaQubit
    pseudoQubit = PseudoQubit
    edge = Edge
    code = "template"
    x_names = ["x", "X", 0, "bit-flip"]
    z_names = ["z", "Z", 1, "phase-flip"]
    dim = 2

    def __init__(
        self,
        size: int,
        dual: bool = True,
        benchmarker: Optional[BenchMarker] = None,
        **kwargs,
    ):
        self.layers = 1
        self.decode_layer = 0
        self.size = size
        self.dual = dual
        self.range = range(size)
        self.benchmarker = benchmarker
        self.no_error = True

        for key, value in kwargs.items():
            setattr(self, key, value)

        self.ancilla_qubits = {}
        self.data_qubits = {}
        self.pseudo_qubits = {}
        self.errors = {}
        self.logical_operators = {}

    def __repr__(self):
        return f"{self.code} {self.size} {self.__class__.__name__}"

    """
    ----------------------------------------------------------------------------------------
                                        Main functions
    ----------------------------------------------------------------------------------------
    """

    def initialize(self, *args, **kwargs) -> None:
        """Initilizes all data objects of the code.

        Error modules may be specified here in the same format as in `init_errors`.

        See Also
        --------
        init_surface
        init_logical_operator
        init_errors
        """
        self.init_surface(**kwargs)
        self.init_logical_operator(**kwargs)
        self.init_errors(*args, **kwargs)

    def simulate(self, z: float = 0, error_order: Optional[List[Error]] = None, **kwargs):
        """Simulate an iteration or errors and measurement.

        Parameters
        ----------
        z : int or float, optional
            Layer of qubits.
        error_order : List of Error, optional
            Order in which the loaded error classes are applied.

        See Also
        --------
        opensurfacesim.error : Error modules.
        apply_errors
        parity_measurement
        """
        self.apply_errors(z=z, apply_order=error_order, **kwargs)
        self.parity_measurement(z=z, **kwargs)

    @property
    def logical_state(self) -> Tuple[List[bool], bool]:
        # Loop over logical operators to find current state
        logical_state = {}
        for key, operator in self.logical_operators.items():
            state = 0
            for ancilla_qubit in operator:
                if ancilla_qubit.state:
                    state = 1 - state
            logical_state[key] = state

        # Compare with previous logical state to find error
        if hasattr(self, "prev_logical_state"):
            logical_error = {}
            for key, state in logical_state.items():
                logical_error[key] = state == self.prev_logical_state[key]
            self.no_error = True if all(logical_error.values()) else False
        else:
            self.no_error = True if all(logical_state.values()) else False
        self.prev_logical_state = logical_state
        return logical_state

    """
    ----------------------------------------------------------------------------------------
                                        Initialization
    ----------------------------------------------------------------------------------------
    """

    @abstractmethod
    def init_surface(self):
        """Inititates the surface code."""
        pass

    @abstractmethod
    def init_logical_operator(self):
        """Inititates the logical operators."""
        pass

    def init_errors(self, *error_modules: Union[str, Error], error_rates: dict = {}) -> None:
        """Initializes error modules.

        Any error module from `opensurfacesim.error` can loaded as either a string equivalent to the module file name or as the module itself. The default error rates for all loaded error modules can be supplied as a dictionary with keywords corresponding to the default error rates of the associated error modules.

        Parameters
        ----------
        args : string or error module
            The error modules to load. May be a string or the loaded module.
        error_rates : dict of floats
            The default error rates for the loaded modules. Must be a dictionary with probabilities with keywords corresponding to the default or overriding error rates of the associated error modules.

        See Also
        --------
        opensurfacesim.error : Error modules.

        Examples
        --------
        Load Pauli and erasure error modules via strings. Set default bit-flip rate to `0.1` and erasure to `0.03`.

            >>> SurfaceCode.init_errors("pauli", "erasure", error_rates={"pauli_x": 0.1, "p_erasure": 0.03})

        Load Pauli error module via module. Set default phase-flip rate to `0.05`.

            >>> import opensurfacesim.error.pauli as pauli
            >>> SurfaceCode.init_errors(pauli, error_rates={"pauli_z": 0.05})
        """
        for error_module in error_modules:
            if type(error_module) == str:
                error_module = importlib.import_module(".errors.{}".format(error_module), package="opensurfacesim")
            error_type = error_module.__name__.split(".")[-1]
            self.errors[error_type] = error_module.Error(**error_rates)

    """
    ----------------------------------------------------------------------------------------
                                        Constructors
    ----------------------------------------------------------------------------------------
    """

    def add_data_qubit(self, loc: Tuple[float, float], z: float = 0, **kwargs) -> DataQubit:
        """Initilizes a data-qubit."""
        data_qubit = self.dataQubit(loc, z)
        data_qubit.edges["x"] = self.edge(data_qubit, "x")
        if self.dual:
            data_qubit.edges["z"] = self.edge(data_qubit, "z")
        self.data_qubits[z][loc] = data_qubit
        return data_qubit

    def add_ancilla_qubit(
        self,
        loc: Tuple[float, float],
        z: float = 0,
        state_type: str = "x",
        **kwargs,
    ) -> AncillaQubit:
        """Initilizes an ancilla-qubit."""
        ancilla_qubit = self.ancillaQubit(loc, z, state_type=state_type)
        self.ancilla_qubits[z][loc] = ancilla_qubit
        return ancilla_qubit

    def add_pseudo_qubit(
        self,
        loc: Tuple[float, float],
        z: float = 0,
        state_type: str = "x",
        **kwargs,
    ) -> PseudoQubit:
        """Initilizes a pseudo-qubit on the boundary."""
        pseudo_qubit = self.pseudoQubit(loc, z, state_type=state_type)
        self.pseudo_qubits[z][loc] = pseudo_qubit
        return pseudo_qubit

    def entangle_pair(
        self,
        data_qubit: DataQubit,
        ancilla_qubit: AncillaQubit,
        key: Union[float, str],
        edge: Optional[Edge] = None,
        **kwargs,
    ) -> None:
        """Entangles one `data_qubit` to a `ancilla_qubit` for parity measurement.

        See Also
        --------
        opensurfacesim.code._template.elements.DataQubit : Data-qubit class.
        opensurfacesim.code._template.elements.AncillaQubit : Ancilla-qubit class.
        opensurfacesim.code._template.elements.Edge : Edge class.
        """
        ancilla_qubit.parity_qubits[key] = data_qubit
        if edge is None:
            edge = data_qubit.edges[ancilla_qubit.state_type]
        edge.add_node(ancilla_qubit)

    """
    ----------------------------------------------------------------------------------------
                                    Errors and Measurement
    ----------------------------------------------------------------------------------------
    """

    def apply_errors(self, z: float = 0, apply_order: Optional[List[Error]] = None, **kwargs) -> None:
        """Applies all errors loaded in the `errors` class attribute to layer `z`.

        If `apply_order` is specified, the error modules are applied in order of the error names in the list. If no order is specified, the errors are applied in a random order. Addionally, any error rate can be overriden by supplying the rate as a keyword argument e.g. `pauli_x = 0.1`.

        Parameters
        ----------
        z : int or float, optional
            Layer of qubits of parity measurments.
        apply_order : list of string, optional
            The order in which the error modules are applied.

        See Also
        --------
        apply_error
        """
        if not apply_order:
            apply_order = self.errors.values()
        for error_class in apply_order:
            for qubit in self.data_qubits[z].values():
                error_class.apply_error(qubit, **kwargs)

    def measure_parity(self, ancilla_qubit: AncillaQubit, **kwargs) -> bool:
        """Applies a parity measurement on the ancilla.

        The functions loops over all the data qubits in the `parity_qubits` attribute of `ancilla_qubit`. For every edge associated with the entangled state on the data qubit, the value of a `parity` boolean is flipped.

        Parameters
        ----------
        ancilla_qubit : AncillaQubit
            The ancilla qubit to apply the parity measurement on.

        Returns
        -------
        parity : bool
            Result of the parity measurment.

        See Also
        --------
        AncillaQubit
        """
        parity = False
        for qubit in ancilla_qubit.parity_qubits.values():
            edge = qubit.edges[ancilla_qubit.state_type]
            if edge.state:
                parity = not parity
        ancilla_qubit.state = parity
        return parity

    def parity_measurement(self, z: float = 0, **kwargs) -> None:
        """Performs a round of parity measurements on layer `z`.

        Parameters
        ----------
        z : int or float, optional
            Layer of qubits of parity measurments.
        """
        for ancilla_qubit in self.ancilla_qubits[z].values():
            self.measure_parity(ancilla_qubit)

    """
    ----------------------------------------------------------------------------------------
                                        Others
    ----------------------------------------------------------------------------------------
    """

    def count_matching_weight(self, z: float = 0, **kwargs) -> int:
        """Counts the number of matchings edges on layer `z`.

        Parameters
        ----------
        z : int or float, optional
            Layer of qubits.
        """
        weight = 0
        for qubit in self.data_qubits[z].values():
            if qubit.edges["x"].matching == 1:
                weight += 1
        if self.dual:
            for qubit in self.data_qubits[z].values():
                if qubit.edges["z"].matching == 1:
                    weight += 1
        return weight

    def reset(self) -> None:
        """Resets the simulator by resetting all of its components."""
        for dlayer in self.data_qubits.values():
            for qubit in dlayer.values():
                qubit.reset()
        for alayer in self.ancilla_qubits.values():
            for qubit in alayer.values():
                qubit.reset()


class FaultyMeasurements(PerfectMeasurements):
    """Simulation template code class for faulty measurements

    Parameters
    ----------
    layers : int, optional
        Number of layers in 3D graph for faulty measurements.
    pseudoEdge : PseudoEdge, optional
        Pseudo edge class.
    pmx : float or int, optional
        Default bit-flip rate during measurements.
    pmz : float or int, optional
        Default phase-flip rate during measurements.
    """

    pseudoEdge = PseudoEdge
    dim = 3

    def __init__(
        self,
        size,
        *args,
        layers: Optional[int] = None,
        pmx: float = 0,
        pmz: float = 0,
        **kwargs,
    ):
        super().__init__(size, *args, **kwargs)
        self.layers = layers if layers else size
        self.decode_layer = self.layers - 1
        self.default_faulty_measurements = dict(pmx=pmx, pmz=pmz)
        self.pseudo_edges = []

    """
    ----------------------------------------------------------------------------------------
                                        Main functions
    ----------------------------------------------------------------------------------------
    """

    def simulate(self, **kwargs):
        """Simulate an iteration or errors and measurement.

        On all but the final layer, the default or overriding error rates (via keyworded arguments) are applied. On the final layer, perfect measurements are applied by setting `pmx=0` and `pmz=0`.
        """
        # Simulate on all but final layers
        for z in range(self.layers):
            super().simulate(z=z, **kwargs)

        # Simulate final layer with perfect measurements
        kwargs.update(dict(pmx=0, pmz=0))
        super().simulate(z=self.decode_layer, **kwargs)

    """
    ----------------------------------------------------------------------------------------
                                        Initialization
    ----------------------------------------------------------------------------------------
    """

    def init_surface(self, **kwargs) -> None:
        """Inititates the surface code.

        The 3D lattice is initilized by first building the ground layer. After that each consecutive layer is built and pseudo-edges are added to connect the ancilla qubits of each layer.
        """
        super().init_surface()
        for z in range(1, self.layers):
            super().init_surface(z=z)
            for upper in self.ancilla_qubits[z].values():
                lower = self.ancilla_qubits[z - 1][upper.loc]
                self.add_vertical_edge(lower, upper)

    def add_vertical_edge(self, lower_ancilla: AncillaQubit, upper_ancilla: AncillaQubit, **kwargs) -> None:
        """Adds a PseudoEdge to connect two instances of an ancilla qubit in time.

        A surface code with faulty measurements must be decoded in 3D. Instances of the same ancilla qubits in time must be connected with an edge. Here, `lower_ancilla` is an older instance of layer `z`, and 'upper_ancilla` is a newer instance of layer `z+1`.

        Parameters
        ----------
        lower_ancilla : AncillaQubit
            Older instance of ancilla (layer `z`).
        upper_ancilla : AncillaQubit
            Newer instance of ancilla (layer `z+1`).

        See Also
        --------
        opensurfacesim.code._template.elementsAncillaQubit : Ancilla-qubit class.
        opensurfacesim.code._template.elementsPseudoEdge : Pseudo-edge class.
        """
        pseudo_edge = self.pseudoEdge(upper_ancilla, edge_type=upper_ancilla.state_type)
        self.pseudo_edges.append(pseudo_edge)
        upper_ancilla.vertical_ancillas["d"] = lower_ancilla
        lower_ancilla.vertical_ancillas["u"] = upper_ancilla
        pseudo_edge.nodes = [upper_ancilla, lower_ancilla]

    """
    ----------------------------------------------------------------------------------------
                                        Measurement
    ----------------------------------------------------------------------------------------
    """

    def parity_measurement(
        self, pmx: Optional[float] = None, pmz: Optional[float] = None, z: float = 0, **kwargs
    ) -> None:
        """Performs a round of parity measurements on layer `z` with faulty measurements.

        On all ancilla qubits of layer `z`, a parity check measurement is performed. Additionally tot he `PerferctMeasurements` class, an additional measurement error is applied, dependent on the type of the ancilla qubit.

        Parameters
        ----------
        pmx : int or float, optional
            Probability of a bit-flip during a parity check measurement.
        pmz : int or float, optional
            Probability of a phase-flip during a parity check measurement.
        z : int or float, optional
            Layer of qubits.
        """
        if pmx is None:
            pmx = self.default_faulty_measurements["pmx"]
        if pmz is None:
            pmz = self.default_faulty_measurements["pmz"]

        for ancilla_qubit in self.ancilla_qubits[z].values():
            self.measure_parity(ancilla_qubit)

            # Apply measurement error
            pM = pmx if ancilla_qubit.state_type in self.x_names else pmz
            if pM != 0 and random.random() < pM:
                ancilla_qubit.state = 1 - ancilla_qubit.state
                ancilla_qubit.mstate = 1

            # Save vertex as anyon if parity different than previous layer
            if "d" in ancilla_qubit.vertical_ancillas:
                lower_state = ancilla_qubit.vertical_ancillas["d"].state
            else:
                lower_state = 0
            ancilla_qubit.state = 0 if ancilla_qubit.state == lower_state else 1

    """
    ----------------------------------------------------------------------------------------
                                        Others
    ----------------------------------------------------------------------------------------
    """

    def count_matching_weight(self, *args, **kwargs) -> int:
        """Counts the number of matchings edges."""
        weight = 0
        for z in self.range:
            weight += super().count_matching_weight(z)
        for pseudo_edge in self.pseudo_edges:
            if pseudo_edge.matching:
                weight += 1
        return weight

    def reset(self, **kwargs):
        """Resets the simulator by resetting all of its components."""
        super().reset()
        for pseudo_edge in self.pseudo_edges:
            pseudo_edge.reset()