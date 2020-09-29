from abc import ABC, abstractmethod
from .elements import DataQubit, AncillaQubit, PseudoQubit, Edge, PseudoEdge
from ...info.benchmark import BenchMarker
from ...error._template import Error
from typing import List, Optional, Union, Tuple
import importlib
import random


numtype = Union[int, float]


class PerfectMeasurements(ABC):
    """Simulation template code class for perfect measurements.

    Parameters
    ----------
    size : int, tuple
        Size of the surface code in single dimension or two dimensions (y,x).
    dual : bool, optional
        Enables the dual graph. Turn off when only simulating for bit-flip errors.
    dataQubit : DataQubit, optional
        Data qubit class.
    ancillaQubit: AncillaQubit, optional
        Ancilla qubit class.
    pseudoQubit : PseudoQubit, optional
        Pseudo qubit class.
    edge : Edge, optional
        Edge class.
    benchmarker : Benchmarker, optional
        Benchmarker class. If a benchmarker class is attached, the benchmarker will start to collect the number of calls of to the code class and decoder class methods.

    See Also
    --------
    DataQubit
    AncillaQubit
    PseudoQubit
    Edge
    Benchmarker
    """

    def __init__(
        self,
        size: int,
        dual: bool = True,
        dataQubit: DataQubit = DataQubit,
        ancillaQubit: AncillaQubit = AncillaQubit,
        pseudoQubit: PseudoQubit = PseudoQubit,
        edge: Edge = Edge,
        benchmarker: Optional[BenchMarker] = None,
        **kwargs,
    ):
        self.dim = 2
        self.size = size
        self.dual = dual
        self.range = range(size)
        self.dataQubit = dataQubit
        self.ancillaQubit = ancillaQubit
        self.pseudoQubit = pseudoQubit
        self.edge = edge
        self.benchmarker = benchmarker
        self.code = str(self.__module__).split(".")[-2]
        self.x_names = ["x", "X", 0, "bit-flip"]
        self.z_names = ["z", "Z", 1, "phase-flip"]
        self.layers = 1
        self.decode_layer = 0

        for key, value in kwargs.items():
            setattr(self, key, value)

        self.ancilla_qubits = {}
        self.data_qubits = {}
        self.pseudo_qubits = {}
        self.errors = {}

    def __repr__(self):
        return f"{self.code} {self.size} {self.__class__.__name__}"

    """
    ----------------------------------------------------------------------------------------
                                        Initialization
    ----------------------------------------------------------------------------------------
    """

    def initialize(self, *args, **kwargs) -> None:
        """Initilizes all data objects of the code."""
        self.init_surface(**kwargs)
        self.init_logical_operator(**kwargs)
        self.logical_state = {key: False for key in self.logical_operators}
        self.init_errors(*args, **kwargs)

    @abstractmethod
    def init_surface(self):
        """Inititates the surface code."""
        pass

    @abstractmethod
    def init_parity_check(self):
        """Inititates a parity check measurement."""
        pass

    @abstractmethod
    def init_logical_operator(self):
        """Inititates the logical operators."""
        pass

    def add_data_qubit(self, loc: Tuple[numtype, numtype], z: numtype = 0, **kwargs) -> DataQubit:
        """Initilizes a data-qubit.

        Parameters
        ----------
        loc : tuple of int, float or string
            Location of the data qubit. Should be in the format of `loc=(x,y)`.
        z : int or float, optional
            Layer of qubit. Required for faulty measurements.

        See Also
        --------
        DataQubit
        """
        data_qubit = self.dataQubit(loc, z)
        data_qubit.edges["x"] = self.edge(data_qubit, "x")
        if self.dual:
            data_qubit.edges["z"] = self.edge(data_qubit, "z")
        self.data_qubits[z][loc] = data_qubit
        return data_qubit

    def add_ancilla_qubit(
        self,
        loc: Tuple[numtype, numtype],
        z: numtype = 0,
        ancilla_type: str = "x",
        **kwargs,
    ) -> AncillaQubit:
        """Initilizes an ancilla-qubit.

        Parameters
        ----------
        loc : tuple of int, float or string
            Location of the ancilla qubit. Should be in the format of `loc=(x,y)`.
        z : int or float, optional
            Layer of qubit. Required for faulty measurements.
        ancilla_type : str, optional
            Basis type of parity checks. Should be either `x` or `z`.

        See Also
        --------
        AncillaQubit
        """
        ancilla = self.ancillaQubit(loc, z, ancilla_type=ancilla_type)
        self.ancilla_qubits[z][loc] = ancilla
        return ancilla

    def add_pseudo_qubit(
        self,
        loc: Tuple[numtype, numtype],
        z: numtype = 0,
        ancilla_type: str = "x",
        **kwargs,
    ) -> PseudoQubit:
        """Initilizes a pseudo-qubit on the boundary.

        Parameters
        ----------
        loc : tuple of int, float or string
            Location of the ancilla qubit. Should be in the format of `loc=(x,y)`.
        z : int or float, optional
            Layer of qubit. Required for faulty measurements.
        ancilla_type : str, optional
            Basis type of parity checks. Should be either `x` or `z`.

        See Also
        --------
        PseudoQubit
        AncillaQubit
        """
        pseudo_qubit = self.pseudoQubit(loc, z, ancilla_type=ancilla_type)
        self.pseudo_qubits[z][loc] = pseudo_qubit
        return pseudo_qubit

    def entangle_pair(
        self,
        data_qubit: DataQubit,
        ancilla_qubit: AncillaQubit,
        key: Union[int, float, str],
        edge: Optional[Edge] = None,
        **kwargs,
    ) -> None:
        """Entangles one `data_qubit` to a `ancilla_qubit` for parity measurement.

        Parameters
        ----------
        data_qubit : DataQubit
            Data qubit.
        ancilla_qubit: AncillaQubit
            Ancilla qubit.
        key : int, float or string
            Key used to store the `data_qubit` in the `ancilla_qubit` .
        edge : Edge, optional
            The `Edge` object related to the state of the `Data_qubit` to entangle to.

        See Also
        --------
        DataQubit
        AncillaQubit
        Edge
        """
        ancilla_qubit.parity_qubits[key] = data_qubit
        if edge is None:
            edge = data_qubit.edges[ancilla_qubit.ancilla_type]
        edge.nodes += [ancilla_qubit]

    """
    ----------------------------------------------------------------------------------------
                                            Errors
    ----------------------------------------------------------------------------------------
    """

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
        Error

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
                error_module = importlib.import_module(".error.{}".format(error_module), package="opensurfacesim")
            error_type = error_module.__name__.split(".")[-1]
            self.errors[error_type] = error_module.Error(self.data_qubits, **error_rates)

    def apply_errors(self, z: numtype = 0, apply_order: Optional[List[Error]] = None, **kwargs: numtype) -> None:

        if not apply_order:
            apply_order = self.errors.values()
        for error_class in apply_order:
            error_class.apply_error_layer(z=z, **kwargs)

    """
    ----------------------------------------------------------------------------------------
                                        Measurement
    ----------------------------------------------------------------------------------------
    """

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
            edge = qubit.edges[ancilla_qubit.ancilla_type]
            if edge.state:
                parity = not parity
        ancilla_qubit.state = parity
        return parity

    def parity_measurement(self, z: numtype = 0, **kwargs) -> None:
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
                                        Simulation
    ----------------------------------------------------------------------------------------
    """

    def simulate(self, z: numtype = 0, **kwargs):
        """Simulate an iteration or errors and measurement.

        Parameters
        ----------
        z : int or float, optional
            Layer of qubits.
        """
        self.apply_errors(z=z, **kwargs)
        self.parity_measurement(z=z, **kwargs)

    def get_logical_state(self, z: numtype = 0, **kwargs) -> Tuple[List[bool], bool]:
        """Returns the logical state on layer `z`.

        Parameters
        ----------
        z : int or float, optional
            Layer of qubits.
        """
        logical_state, logical_error = {}, {}

        for key, operator in self.logical_operators.items():
            state = 0
            for ancilla_qubit in operator:
                if ancilla_qubit.state:
                    state = 1 - state
            logical_state[key] = state
            logical_error[key] = state == self.logical_state[key]

        no_error = True if all(logical_error.values()) else False
        self.logical_state = logical_state
        return logical_state, no_error

    def count_matching_weight(self, z: numtype = 0, **kwargs) -> int:
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
    pseudoEdge: PseudoEdge, optional
        Pseudo edge class.
    """

    def __init__(
        self,
        size,
        *args,
        layers: Optional[int] = None,
        pseudoEdge: PseudoEdge = PseudoEdge,
        pmx: numtype = 0,
        pmz: numtype = 0,
        **kwargs,
    ):
        super().__init__(size, *args, dim=3, **kwargs)

        self.layers = layers if layers else size
        self.decode_layer = self.layers - 1
        self.default_faulty_measurements = dict(pmx=pmx, pmz=pmz)
        self.pseudoEdge = pseudoEdge
        self.pseudo_edges = []

    """
    ----------------------------------------------------------------------------------------
                                        Initialization
    ----------------------------------------------------------------------------------------
    """

    def initialize(self, *args, **kwargs) -> None:
        """Initilizes all data objects of the code."""
        self.init_surface(**kwargs)
        self.init_logical_operator(**kwargs)
        self.logical_state = {key: False for key in self.logical_operators}
        self.default_faulty_measurements = {
            key: kwargs.pop(key, self.default_faulty_measurements[key]) for key in ["pmx", "pmz"]
        }
        self.init_errors(*args, **kwargs)

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
        """Adds a `PseudoEdge` to connect two instances of an ancilla qubit in time.

        A surface code with faulty measurements must be decoded in 3D. Instances of the same ancilla qubits in time must be connected with an edge. Here, `lower_ancilla` is an older instance of layer `z`, and 'upper_ancilla` is a newer instance of layer `z+1`.

        Parameters
        ----------
        lower_ancilla : AncillaQubit
            Older instance of ancilla (layer `z`).
        upper_ancilla : AncillaQubit
            Newer instance of ancilla (layer `z+1`).

        See Also
        --------
        AncillaQubit
        PseudoEdge
        """
        pseudo_edge = self.pseudoEdge(upper_ancilla, Type=upper_ancilla.ancilla_type)
        self.pseudo_edges.append(pseudo_edge)
        upper_ancilla.vertical_ancillas["d"] = lower_ancilla
        upper_ancilla.vertical_edges["d"] = pseudo_edge
        lower_ancilla.vertical_ancillas["u"] = upper_ancilla
        lower_ancilla.vertical_edges["u"] = pseudo_edge
        pseudo_edge.nodes = [upper_ancilla, lower_ancilla]

    """
    ----------------------------------------------------------------------------------------
                                        Measurement
    ----------------------------------------------------------------------------------------
    """

    def parity_measurement(
        self, pmx: Optional[numtype] = None, pmz: Optional[numtype] = None, z: numtype = 0, **kwargs
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
            pM = pmx if ancilla_qubit.ancilla_type in self.x_names else pmz
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
                                        Simulation
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

    def get_logical_state(self, **kwargs) -> Tuple[List[bool], bool]:
        """Returns the logical state on the decode layer."""
        return super().get_logical_state(z=self.decode_layer)

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