from abc import ABC, abstractmethod
from typing import List, Optional, Tuple, Union
from ..configuration import flatten_dict, init_config
from ..codes._template.sim import PerfectMeasurements
from ..codes.elements import AncillaQubit, Edge, PseudoQubit
from collections import defaultdict
from matplotlib.lines import Line2D
from pathlib import Path

LA = List[AncillaQubit]
LTAP = List[Tuple[AncillaQubit, PseudoQubit]]


class SimCode(ABC):
    """
    Decoder simulation class template.

    Parameters
    ----------
    code
        A ``PerfectMeasurements`` or ``FaultyMeasurements`` class from the `sim` module of :doc:`../codes/index`.
    check_compatibility
        Checks compatibility of the decoder with the code class and loaded errors by `check_compatibility`.

    Attributes
    ----------
    compatibililty_measurements : dict
        Compatibility with perfect or faulty measurements.
    compatibility_errors : dict
        Compatibility with the various error modules in :doc:`../errors/index`.

    """

    name = ("Template simulation decoder",)
    short = "template"

    compatibility_measurements = dict(
        PerfectMeasurements=True,
        FaultyMeasurements=True,
    )
    compatibility_errors = dict(
        pauli=True,
        erasure=True,
    )

    def __init__(self, code: PerfectMeasurements, check_compatibility: bool = False, **kwargs):

        self.code = code
        self.config_file = Path(__file__).resolve().parent / "decoders.ini"
        self.config = init_config(self.config_file)[self.short]
        self.config.update(kwargs)

        if check_compatibility:
            self.check_compatibility()

    def __repr__(self):
        return "{} decoder ({})".format(self.name, self.__class__.__name__)

    def check_compatibility(self):
        """Checks compatibility of the decoder with the code class and loaded errors."""
        compatible, unspecified = True, False
        code = self.code.__class__.__module__.split(".")[-2]
        measurement = self.code.__class__.__name__
        decoder = self.__class__.__name__.split(".")[-1]
        if str(code).capitalize() != decoder:
            print(f"❕ Code <{code}> loaded with <{decoder}> decoder class.")

        if measurement in self.compatibility_measurements:
            if not self.compatibility_measurements[measurement]:
                print(f"❌ Type <{measurement}> is not compatible with this decoder")
                compatible = False
        else:
            print(f"❔ Type <{measurement}> compatibility unspecified")
            unspecified = True
        for name in self.code.errors:
            if name in self.compatibility_errors:
                if not self.compatibility_errors[name]:
                    print(f"❌ Error module <{name}> is not compatible with this decoder")
                    compatible = False
            else:
                print(f"❔ Error Module <{name}> compatibility unspecified")
                unspecified = True
        if compatible and not unspecified:
            print("✅ This decoder is compatible with the code.")

    @staticmethod
    def get_neighbor(ancilla_qubit: AncillaQubit, key: str) -> Tuple[AncillaQubit, Edge]:
        """Returns the neighboring ancilla-qubit of ``ancilla_qubit`` in the direction of ``key``."""
        data_qubit = ancilla_qubit.parity_qubits[key]
        edge = data_qubit.edges[ancilla_qubit.state_type]
        neighbor = edge.nodes[not edge.nodes.index(ancilla_qubit)]
        return neighbor, edge

    def get_neighbors(self, ancilla_qubit: AncillaQubit, loop: bool = False, **kwargs):
        """Returns all neighboring ancillas, including other time instances.

        Parameters
        ----------
        loop
            Include looped neighbors.
        """
        neighbors = {}
        for key in ancilla_qubit.parity_qubits:
            neighbors[key] = self.get_neighbor(ancilla_qubit, key)
        for ancilla, edge in ancilla_qubit.vertical_edges.items():
            if loop or abs(ancilla.z - ancilla_qubit.z) == 1:
                neighbors[ancilla.z - ancilla_qubit.z] = (ancilla, edge)    
        return neighbors

    def correct_edge(self, ancilla_qubit: AncillaQubit, key: str, **kwargs) -> AncillaQubit:
        """Applies a correction.

        The correction is applied to the data-qubit located at ``ancilla_qubit.parity_qubits[key]``. More specifically, the correction is applied to the `~.codes.elements.Edge` object corresponding to the ``state_type`` of ``ancilla_qubit``.
        """
        (next_qubit, edge) = self.get_neighbor(ancilla_qubit, key)
        edge.state = 1 - edge.state
        return next_qubit

    def get_syndrome(self, find_pseudo: bool = False) -> Union[Tuple[LA, LA], Tuple[LTAP, LTAP]]:
        """Finds the syndrome of the code.

        Parameters
        ----------
        find_pseudo : bool, optional
            If enabled, the lists of syndromes returned are not only `~.codes.elements.AncillaQubit`\ s, but tuples of ``(ancilla, pseudo)``, where ``pseudo`` is the closest `~.codes.elements.PseudoQubit` in the boundary of the code.

        Returns
        -------
        list
            Plaquette operator syndromes.
        list
            Star operator syndromes.
        """
        plaqs, stars = [], []
        if find_pseudo is False:
            for ancilla in [
                ancilla
                for layer in self.code.ancilla_qubits.values()
                for ancilla in layer.values()
                if ancilla.syndrome
            ]:
                if ancilla.state_type == "x":
                    plaqs.append(ancilla)
                elif ancilla.state_type == "z":
                    stars.append(ancilla)
        else:
            for ancilla in [
                ancilla
                for layer in self.code.ancilla_qubits.values()
                for ancilla in layer.values()
                if ancilla.syndrome
            ]:
                if ancilla.state_type == "x":
                    if ancilla.loc[0] < self.code.size[0] / 2:
                        pseudo = self.code.pseudo_qubits[ancilla.z][(0, ancilla.loc[1])]
                    else:
                        pseudo = self.code.pseudo_qubits[ancilla.z][
                            (self.code.size[0], ancilla.loc[1])
                        ]
                    plaqs.append((ancilla, pseudo))
                else:
                    if ancilla.loc[1] < self.code.size[1] / 2:
                        pseudo = self.code.pseudo_qubits[ancilla.z][(ancilla.loc[0], -0.5)]
                    else:
                        pseudo = self.code.pseudo_qubits[ancilla.z][
                            (ancilla.loc[0], self.code.size[1] - 0.5)
                        ]
                    stars.append((ancilla, pseudo))
        return plaqs, stars

    @abstractmethod
    def decode(self, *args, **kwargs):
        """Decodes the surface loaded at ``self.code`` after all ancilla-qubits have been measured."""
        pass


class PlotCode(SimCode):
    """Decoder plotting class template.

    The plotting class initiates a `opensurfacesim.plot` object. For its usage, see :ref:`plot-usage`.
    """

    name = ("Template plot decoder",)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        if hasattr(self.code, "figure"):
            self.rc = self.code.figure.rc
        else:
            file = Path(__file__).resolve().parent.parent / "plot.ini"
            self.rc = flatten_dict(init_config(file))

        self.line_color_normal = {
            "x": dict(color=self.rc["color_edge"]),
            "z": dict(color=self.rc["color_edge"]),
        }
        self.line_color_match = {
            "x": dict(color=self.rc["color_x_secondary"]),
            "z": dict(color=self.rc["color_z_secondary"]),
        }
        self.matching_lines = defaultdict(bool)

    def decode(self, *args, **kwargs):
        # Inherited docstrings
        self.matching_lines = defaultdict(bool)
        super().decode(*args, **kwargs)
        if hasattr(self.code, "figure"):
            self.code.figure.draw_figure(new_iter_name="Matchings found")

    def correct_edge(self, qubit, key, **kwargs):
        # Inherited docstring
        (next_qubit, edge) = self.get_neighbor(qubit, key)
        edge.state = not edge.state
        if hasattr(qubit, "surface_lines"):
            self.plot_matching_edge(qubit.surface_lines.get(key, None))
        if hasattr(next_qubit, "surface_lines"):
            self.plot_matching_edge(next_qubit.surface_lines.get(tuple([-i for i in key]), None))
        return next_qubit

    def plot_matching_edge(self, line: Optional[Line2D] = None):
        """Plots the matching edge.

        Based on the colors defined in ``self.line_color_match``, if a `~matplotlib.lines.Line2D` object is supplied, the color of the edge is changed. A future change back to its original color is immediately saved in ``figure.future_dict``.
        """
        if line:
            iteration = self.code.figure.history_iter
            state_type = line.object.state_type
            self.matching_lines[line] = not self.matching_lines[line]
            if self.matching_lines[line]:
                self.code.figure.future_dict[iteration + 1][line] = self.line_color_match[
                    state_type
                ]
                self.code.figure.future_dict[iteration + 2][line] = self.line_color_normal[
                    state_type
                ]
            else:
                self.code.figure.future_dict[iteration + 1].pop(line, None)
                self.code.figure.future_dict[iteration + 2].pop(line, None)
