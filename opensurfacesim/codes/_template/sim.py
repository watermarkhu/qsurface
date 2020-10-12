from abc import ABC, abstractmethod
from ..elements import DataQubit, AncillaQubit, PseudoQubit, Edge, PseudoEdge
from ...benchmark import BenchMarker
from ...errors._template import Sim as Error
from typing import List, Optional, Union, Tuple
import importlib
import random


class PerfectMeasurements(ABC):
    """Simulation template code class for perfect measurements.

    The qubits of the code class are stored in a double dictionary, with the keys in the outer dictionary corresponding to the qubit layer. For perfect measurements, there is a single layer. For faulty measurements, there are multiple layers (and defaults to ``self.size``). In the nested dictionaries each qubit is stored by ``qubit.loc`` as key. A qubit can thus be accessed by ``self.qubits[layer][(x,y)]``.

    The qubit and edge classes from :doc:`elements` can be replaced with inherited classes to store decoder dependent attributes.

    Parameters
    ----------
    size : int or tuple 
        Size of the surface code in single dimension or two dimensions ``(x,y)``.
    benchmarker : `~opensurfacesim.benchmark.Benchmarker`, optional
        If a benchmarker class is attached, the benchmarker will start to collect the number of calls of to the code class and decoder class methods.

    Attributes
    ----------
    dataQubit : `~opensurfacesim.code.elements.AncillaQubit`
        Data-qubit class to use for the current code. 

    ancillaQubit : `~opensurfacesim.code.elements.DataQubit`
        Ancilla-qubit class to use for the current code. 

    pseudoQubit : `~opensurfacesim.code.elements.PseudoQubit`
        Pseudo-qubit class to use for the current code.

    edge : `~opensurfacesim.code.elements.Edge`
        Edge class to use for the current code.

    ancilla_qubits : dict of dict 
        Nested dictionary of `~opensurfacesim.code.elements.AncillaQubit`\ s.

    data_qubits : dict of dict 
        Nested dictionary of `~opensurfacesim.code.elements.DataQubit`\ s.

    pseudo_qubits : dict of dict 
        Nested dictionary of `~opensurfacesim.code.elements.PseudoQubit`\ s.

    errors : dict
        Dictionary of error modules with the module name as key. All error modules from :doc:`../errors/index` loaded in ``self.errors`` will be applied during a simulation by :meth:`random_errors`.

    logical_operators : dict of list
        Dictionary with lists of `~opensurfacesim.code.elements.Edge`\ s that from a trivial loop over the surface and correspond to a logical operator. The logical state of each operator can be obtained by the state of each Edge in the list.

    logical_state : dict of bool
        Dictionary with the states corresponding to the logical operators in ``self.logical_operators``.

    no_error : bool
        Indicator for whether there is a logical error in the last iteration. The value for ``self.no_error`` is updated after a call to ``self.logical_state``.
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
        size: Union[int, Tuple[int, int]],
        benchmarker: Optional[BenchMarker] = None,
        **kwargs,
    ):
        self.layers = 1
        self.decode_layer = 0
        self.size = size if type(size) == tuple else (size, size)
        self.benchmarker = benchmarker
        self.no_error = True
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.ancilla_qubits = {}
        self.data_qubits = {}
        self.pseudo_qubits = {}
        self.errors = {}
        self.logical_operators = {}

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
            self.no_error = True if not any(logical_state.values()) else False
        self.prev_logical_state = logical_state
        return logical_state

    def __repr__(self):
        return f"{self.code} {self.size} {self.__class__.__name__}"

    """
    ----------------------------------------------------------------------------------------
                                        Initialization
    ----------------------------------------------------------------------------------------
    """
    def initialize(self, *args, **kwargs):
        """Initializes all data objects of the code.

        Builds the surface with `init_surface`, adds the logical operators with `init_logical_operator`, and loads error modules with `init_errors`. All keyword arguments from these methods can be used for `initialize`.
        """
        self.init_surface(**kwargs)
        self.init_logical_operator(**kwargs)
        self.init_errors(*args, **kwargs)

    @abstractmethod
    def init_surface(self):
        """Initiates the surface code."""
        pass

    @abstractmethod
    def init_logical_operator(self):
        """Initiates the logical operators."""
        pass


    def init_errors(
        self, *error_modules: Union[str, Error], error_rates: dict = {}
    ):
        """Initializes error modules.

        Any error module from :doc:`../errors/index` can loaded as either a string equivalent to the module file name or as the module itself. The default error rates for all loaded error modules can be supplied as a dictionary with keywords corresponding to the default error rates of the associated error modules.

        Parameters
        ----------
        args : string or error module
            The error modules to load. May be a string or the loaded module.
        error_rates : dict of floats
            The default error rates for the loaded modules. Must be a dictionary with probabilities with keywords corresponding to the default or overriding error rates of the associated error modules.


        Examples
        --------
        Load :doc:`../errors/pauli` and :doc:`../errors/erasure/` modules via string names. Set default bit-flip rate to `0.1` and erasure to `0.03`.

            >>> SurfaceCode.init_errors(
            ...    "pauli", 
            ...    "erasure",
            ...    error_rates={"p_bitflip": 0.1, "p_erasure": 0.03}
            ... )

        Load Pauli error module via module. Set default phase-flip rate to `0.05`.

            >>> import opensurfacesim.error.pauli as pauli
            >>> SurfaceCode.init_errors(pauli, error_rates={"p_phaseflip": 0.05})
        """
        for error_module in error_modules:
            if type(error_module) == str:
                error_module = importlib.import_module(
                    ".errors.{}".format(error_module), package="opensurfacesim"
                )
            self._init_error(error_module, error_rates)

    def _init_error(self, error_module, error_rates):
        """Initializes the ``Sim`` class of a error module."""
        error_type = error_module.__name__.split(".")[-1]
        self.errors[error_type] = error_module.Sim(**error_rates)


    """
    ----------------------------------------------------------------------------------------
                                        Constructors
    ----------------------------------------------------------------------------------------
    """

    def add_data_qubit(
        self, loc: Tuple[float, float], z: float = 0, **kwargs
    ) -> DataQubit:
        """Initializes a `~.code.elements.DataQubit` with `dataQubit` and `edge`, and saved to ``self.data_qubits[z][loc]``."""
        data_qubit = self.dataQubit(loc, z)
        data_qubit.edges["x"] = self.edge(data_qubit, "x")
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
        """Initializes a `~.code.elements.AncillaQubit` with `ancillaQubit`, and saved to ``self.ancilla_qubits[z][loc]``."""
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
        """Initializes a `~.code.elements.PseudoQubit` with `pseudoQubit`, and saved to ``self.pseudo_qubits[z][loc]``."""
        pseudo_qubit = self.pseudoQubit(loc, z, state_type=state_type)
        self.pseudo_qubits[z][loc] = pseudo_qubit
        return pseudo_qubit

    @staticmethod
    def entangle_pair(
        data_qubit: DataQubit,
        ancilla_qubit: AncillaQubit,
        key: Union[float, str],
        edge: Optional[Edge] = None,
        **kwargs,
    ):
        """Entangles one `~.code.elements.DataQubit` to a `~.code.elements.AncillaQubit` for parity measurement.

        Parameters
        data_qubit : `~.code.elements.DataQubit`
            Control qubit.
        ancilla_qubit : `~.code.elements.AncillaQubit`
            Controlled qubit.
        key : float or str
            The entanglement is saved by adding the `~.code.elements.DataQubit` to `~.code.elements.AncillaQubit`\ ``.parity_qubits[key]``
        edge : `~.code.elements.Edge`, optional
            The edge of the data-qubit to entangle to.
        """
        ancilla_qubit.parity_qubits[key] = data_qubit
        if edge is None:
            edge = data_qubit.edges[ancilla_qubit.state_type]
        edge.add_node(ancilla_qubit)

    """
    ----------------------------------------------------------------------------------------
                                            Errors
    ----------------------------------------------------------------------------------------
    """

    def random_errors(
        self, z: float = 0, apply_order: Optional[List[Error]] = None, **kwargs
    ):
        """Applies all errors loaded in ``self.errors`` attribute to layer ``z``.

        The random error is applied for each loaded error module by calling ``error_module.random_error()``. If ``apply_order`` is specified, the error modules are applied in order of the error names in the list. If no order is specified, the errors are applied in a random order. Addionally, any error rate can set by supplying the rate as a keyword argument e.g. ``p_bitflip = 0.1``.

        Parameters
        ----------
        z : int or float, optional
            Layer of qubits of parity measurements.
        apply_order : list of string, optional
            The order in which the error modules are applied.
        """
        if not apply_order:
            apply_order = self.errors.values()
        for error_class in apply_order:
            for qubit in self.data_qubits[z].values():
                error_class.random_error(qubit, **kwargs)

    # @staticmethod
    # def measure_parity(ancilla_qubit: AncillaQubit, **kwargs) -> bool:
    #     """Applies a parity measurement on the ancilla.

    #     The functions loops over all the data qubits in the `parity_qubits` attribute of `ancilla_qubit`. For every edge associated with the entangled state on the data qubit, the value of a `parity` boolean is flipped.

    #     Parameters
    #     ----------
    #     ancilla_qubit : AncillaQubit
    #         The ancilla qubit to apply the parity measurement on.

    #     Returns
    #     -------
    #     parity : bool
    #         Result of the parity measurment.

    #     See Also
    #     --------
    #     AncillaQubit
    #     """
    #     parity = False
    #     for qubit in ancilla_qubit.parity_qubits.values():
    #         edge = qubit.edges[ancilla_qubit.state_type]
    #         if edge.state:
    #             parity = not parity
    #     ancilla_qubit.state = parity
    #     return parity

    # def parity_measurement(self, z: float = 0, **kwargs):
    #     """Performs a round of parity measurements on layer `z`.

    #     Parameters
    #     ----------
    #     z : int or float, optional
    #         Layer of qubits of parity measurments.
    #     """
    #     for ancilla_qubit in self.ancilla_qubits[z].values():
    #         self.measure_parity(ancilla_qubit)

    """
    ----------------------------------------------------------------------------------------
                                        Others
    ----------------------------------------------------------------------------------------
    """

    def reset(self):
        """Resets the simulator by resetting all of its components."""
        for dlayer in self.data_qubits.values():
            for qubit in dlayer.values():
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

        if layers:
            self.layers = layers
        else:
            self.layers = max(size) if type(size) == tuple else size
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

    def init_surface(self, **kwargs):
        """Initiates the surface code.

        The 3D lattice is initilized by first building the ground layer. After that each consecutive layer is built and pseudo-edges are added to connect the ancilla qubits of each layer.
        """
        super().init_surface()
        for z in range(1, self.layers):
            super().init_surface(z=z)
            for upper in self.ancilla_qubits[z].values():
                lower = self.ancilla_qubits[z - 1][upper.loc]
                self.add_vertical_edge(lower, upper)

    def add_vertical_edge(
        self, lower_ancilla: AncillaQubit, upper_ancilla: AncillaQubit, **kwargs
    ):
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
        opensurfacesim.code.elementsAncillaQubit : Ancilla-qubit class.
        opensurfacesim.code.elementsPseudoEdge : Pseudo-edge class.
        """
        pseudo_edge = self.pseudoEdge(upper_ancilla, state_type=upper_ancilla.state_type)
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
        self,
        pmx: Optional[float] = None,
        pmz: Optional[float] = None,
        z: float = 0,
        **kwargs,
    ):
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

    def reset(self, **kwargs):
        """Resets the simulator by resetting all of its components."""
        super().reset()
        for pseudo_edge in self.pseudo_edges:
            pseudo_edge.reset()