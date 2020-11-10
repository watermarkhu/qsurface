from abc import ABC, abstractmethod
from typing import List, Optional, Tuple, Union
from collections import defaultdict
from matplotlib.lines import Line2D
from pathlib import Path
import configparser
import ast
import os
from ..codes._template.sim import PerfectMeasurements
from ..codes.elements import AncillaQubit, Edge, PseudoQubit


LA = List[AncillaQubit]
LTAP = List[Tuple[AncillaQubit, PseudoQubit]]


def write_config(config_dict: dict, path: str):
    """Writes a configuration file to the path.

    Parameters
    ----------
    config_dict : dict
        Dictionary of configuration parameters. Can be nested.
    path : str
        Path to the file. Must include the desired extension.
    """
    config = configparser.ConfigParser()

    for key, value in config_dict.items():
        if type(value) == dict:
            config[key] = value
        else:
            config["main"][key] = value

    with open(path, "w") as configfile:
        config.write(configfile)


def read_config(path: Path, config_dict: Optional[dict] = None) -> dict:
    """Reads an INI formatted configuration file and parses it to a nested dict

    Each category in the INI file will be parsed as a separate nested dictionary. A default `config_dict` can be provided with default values for the parameters. Parameters under the "main" section will be parsed in the main dictionary. All data types will be converted by `ast.literal_eval()`.

    Parameters
    ----------
    path : str
        Path to the file. Must include the desired extension.
    config_dict : dict, optional
        Nested dictionary of default parameters

    Returns
    -------
    dict
        Parsed dictionary.

    Examples
    --------
    Let us look at the following example INI file.

    .. code-block:: text

        [main]
        param1 = hello

        [section]
        param2 = world
        param3 = 0.1

    This file will be parsed as follows

        >>> read_config("config.ini")
        {
            "param1": "hello",
            "section": {
                "param2": "world",
                "param3": 0.1
            }
        }
    """
    if config_dict is None:
        config_dict = defaultdict(dict)

    config = configparser.ConfigParser()
    config.read(path)

    for section_name, section in config._sections.items():
        section_config = config_dict if section_name == "main" else config_dict[section_name]
        for key, item in section.items():
            try:
                section_config[key] = ast.literal_eval(item)
            except:
                section_config[key] = item
    return config_dict


def init_config(ini_file, write: bool = False, **kwargs):
    """Reads the default and the user defined INI file.

    First, the INI file stored in file directory is read and parsed. If there exists another INI file in the working directory, the attributes defined there are read, parsed and overwrites and default values.

    Parameters
    ----------
    write : bool
        Writes the default configuration to the working direction of the user.

    See Also
    --------
    write_config
    read_config
    """
    config_dict = read_config(ini_file)
    config_path = Path.cwd() / ini_file.name
    if write:
        write_config(config_dict, config_path)
    if os.path.exists(config_path):
        read_config(config_path, config_dict)
    return config_dict


class Sim(ABC):
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
    compatibility_measurements : dict
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
        return "<{} decoder ({})>".format(self.name, self.__class__.__name__)

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
            Include neighbors in time that are not chronologically next to each other during decoding within the same instance.
        """
        neighbors = {}
        for key in ancilla_qubit.parity_qubits:
            neighbors[key] = self.get_neighbor(ancilla_qubit, key)
        for ancilla, edge in ancilla_qubit.z_neighbors.items():
            if loop or abs(ancilla.z - ancilla_qubit.z) == 1:
                neighbors[ancilla.z - ancilla_qubit.z] = (ancilla, edge)
        return neighbors

    def correct_edge(self, ancilla_qubit: AncillaQubit, key: str, **kwargs) -> AncillaQubit:
        """Applies a correction.

        The correction is applied to the data-qubit located at ``ancilla_qubit.parity_qubits[key]``. More specifically, the correction is applied to the `~.codes.elements.Edge` object corresponding to the ``state_type`` of ``ancilla_qubit``.
        """
        (next_qubit, edge) = self.get_neighbor(ancilla_qubit, key)
        edge.state = not edge.state
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
                ancilla for layer in self.code.ancilla_qubits.values() for ancilla in layer.values() if ancilla.syndrome
            ]:
                if ancilla.state_type == "x":
                    plaqs.append(ancilla)
                elif ancilla.state_type == "z":
                    stars.append(ancilla)
        else:
            for ancilla in [
                ancilla for layer in self.code.ancilla_qubits.values() for ancilla in layer.values() if ancilla.syndrome
            ]:
                if ancilla.state_type == "x":
                    if ancilla.loc[0] < self.code.size[0] / 2:
                        pseudo = self.code.pseudo_qubits[ancilla.z][(0, ancilla.loc[1])]
                    else:
                        pseudo = self.code.pseudo_qubits[ancilla.z][(self.code.size[0], ancilla.loc[1])]
                    plaqs.append((ancilla, pseudo))
                else:
                    if ancilla.loc[1] < self.code.size[1] / 2:
                        pseudo = self.code.pseudo_qubits[ancilla.z][(ancilla.loc[0], -0.5)]
                    else:
                        pseudo = self.code.pseudo_qubits[ancilla.z][(ancilla.loc[0], self.code.size[1] - 0.5)]
                    stars.append((ancilla, pseudo))
        return plaqs, stars

    @abstractmethod
    def decode(self, *args, **kwargs):
        """Decodes the surface loaded at ``self.code`` after all ancilla-qubits have been measured."""
        pass


class Plot(Sim):
    """Decoder plotting class template.

    The plotting decoder class requires a surface code object that inherits from `.codes._template.plot.PerfectMeasurements`. The template decoder provides the `plot_matching_edge` method that is called by `correct_edge` to visualize the matched edges on the lattice.

    parameters
    ----------
    args, kwargs
        Positional and keyword arguments are passed on to `~.decoders._template.Sim`.

    attributes
    ----------
    line_color_match : dict
        Plot properties for matched edges.
    line_color_normal : dict
        Plot properties for normal edges.
    matching_lines : defaultdict(bool)
        Dictionary of edges that have been added to the matching.
    """

    name = ("Template plot decoder",)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        if hasattr(self.code, "figure"):
            self.params = self.code.figure.params

        self.line_color_match = {
            "x": {"color": self.params.color_x_secondary},
            "z": {"color": self.params.color_z_secondary},
        }
        self.line_color_normal = {
            "x": {"color": self.params.color_edge},
            "z": {"color": self.params.color_edge},
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
        next_qubit = super().correct_edge(qubit, key, **kwargs)
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
                self.code.figure.future_dict[iteration + 1][line] = self.line_color_match[state_type]
                self.code.figure.future_dict[iteration + 2][line] = self.line_color_normal[state_type]
            else:
                self.code.figure.future_dict[iteration + 1].pop(line, None)
                self.code.figure.future_dict[iteration + 2].pop(line, None)
