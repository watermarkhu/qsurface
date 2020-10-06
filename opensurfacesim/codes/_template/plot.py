from typing import List, Optional, Tuple
from matplotlib import transforms
from matplotlib.lines import Line2D
import matplotlib.pyplot as plt
from matplotlib.pyplot import plot
from ...configuration import get_attributes
from ...plot._template import Template2D as TemplatePlotPM
from .sim import PerfectMeasurements as TemplateSimPM, FaultyMeasurements as TemplateSimFM


class CodePlotPM(TemplatePlotPM):
    """Template surface code plot for perfect measurements.

    Parameters
    ----------
    code : `opensurfacesim.<code>.plot.PerfectMeasurements` class
        The `PerfectMeasurments` class from the `plot` module of any code, e.g. toric.
    """

    main_boundary = None
    legend_loc = (1, 1)
    base_properties = {
        "data_qubit": {
            "facecolor": "color_qubit_face",
            "edgecolor": "color_qubit_edge",
        },
        "x_ancilla_0": {
            "facecolor": "color_qubit_face",
            "edgecolor": "color_qubit_edge",
        },
        "x_ancilla_1": {
            "edgecolor": "color_qubit_edge",
            "facecolor": "color_x_secundary",
        },
        "z_ancilla_0": {
            "facecolor": "color_qubit_face",
            "edgecolor": "color_qubit_edge",
        },
        "z_ancilla_1": {
            "facecolor": "color_z_secundary",
            "edgecolor": "color_qubit_edge",
        },
    }

    def __init__(self, code: TemplateSimPM, plot_properties: dict, *args, **kwargs) -> None:
        self.code = code
        super().__init__(*args, init_plot=False, **kwargs)
        plot_properties.update(self.base_properties)
        self.init_properties(plot_properties)
        self.init_plot()

    def init_legend(
        self, legend_loc: Tuple[float, float], items: List[Line2D] = [], **kwargs
    ) -> None:
        """Initilizes the legend of the main axis of the figure.

        The legend of the main axis `main_ax` constists of a series of matplotlib.line.Line2D objects. The qubit, vertex and plaquettes are always in the legend for a surface code plot. Any error loaded in the code at `code.errors` will add an extra element to the legend for differentiation if an error occurs. The 'Line2D' attributes are stored at `Error.legend_attributes` of the `Error` class. Additional items can be added via the `items` argument.

        Parameters
        ----------
        legend_loc : tuple of float or int
            Relative position to the main axis `main_ax`.
        items : list of matplotlib.lines.Line2D, optional
            Additional elements to the legend.

        See Also
        --------
        opensurfacesim.error._template.Error : Template error module.
        _legend_circle : creates a matplotlib.line.Line2D object.
        """
        # Main legend items
        self.lh = [
            self._legend_circle(
                "Vertex",
                ls="-",
                color=self.color_edge,
                mfc=self.color_qubit_face,
                mec=self.color_qubit_edge,
                marker="s",
                ms=5,
            ),
            self._legend_circle(
                "Plaquette",
                ls="--",
                color=self.color_edge,
                mfc=self.color_qubit_face,
                mec=self.color_qubit_edge,
                marker="D",
                ms=5,
            ),
            self._legend_circle("Qubit", mec=self.color_qubit_edge, mfc=self.color_qubit_face),
        ]
        item_names = ["Vertex", "Plaquette"]
        # Error legend items
        for error in self.code.errors.values():
            for name, attribute_names in error.legend_attributes.items():
                if name not in item_names:
                    attributes = get_attributes(self, attribute_names, name=name)
                    self.lh.append(self._legend_circle(name, **attributes))
                    item_names.append(name)

        self.lh += items
        if legend_loc:
            self.main_ax.legend(handles=self.lh, bbox_to_anchor=legend_loc, **kwargs)

    def init_plot(self, **kwargs) -> None:
        title = "{} lattice".format(str(self.code.__class__.__module__).split(".")[-2])
        self.init_axis(self.main_boundary, title=title)
        self.init_legend(self.legend_loc, loc="upper right", ncol=1)
        for item in self.code.data_qubits[0].values():
            self._plot_data(item)
        for item in self.code.ancilla_qubits[0].values():
            self._plot_ancilla(item)
        # if self.code.pseudo_qubits:
        #     for item in self.code.pseudo_qubits[0].values():
        #         self._plot_ancilla(item)
        self.draw_figure()

    def parse_boundary_coordinates(self, size, *args: float) -> List[float]:
        """Parse two locations on the lattice.

        An unbounded surface cannot be plotted on a 2D figure. The lines on the boundary consisting of two coordinates must thus be parsed such that all lines will be plotted within the given window.

        Parameters
        ----------
        args : int or float
            Coordinates.

        Returns
        -------
        list of int or float
            Parsed coordinates
        """
        return args

    def _plot_ancilla(self, item):
        """plots an ancilla-qubit.

        For an ancilla-qubit, a line is plotted towards each of the data-qubits in the `parity_qubits` attribute.
        """
        linestyles = {"x": self.line_style_primary, "z": self.line_style_secundary}
        rotations = {"x": 0, "z": 45}
        
        trans = {
            "x": self.main_ax.transData
            + transforms.ScaledTranslation(
                -self.patch_rectangle_2d / 2,
                self.patch_rectangle_2d / 2,
                self.figure.dpi_scale_trans,
            ),
            "z": self.main_ax.transData
            + transforms.ScaledTranslation(
                0, self.patch_rectangle_2d / 2, self.figure.dpi_scale_trans
            ),
        }

        item.surface_lines = {}
        for key, data in item.parity_qubits.items():
            line = Line2D(
                self.parse_boundary_coordinates(self.code.size[0], item.loc[0], data.loc[0]),
                self.parse_boundary_coordinates(self.code.size[1], item.loc[1], data.loc[1]),
                ls=linestyles[item.state_type],
                zorder=0,
                lw=self.line_width_primary,
                color=self.color_edge,
            )
            item.surface_lines[key] = line
            self.main_ax.add_artist(line)
            line.object = item
        item.surface_plot = plt.Rectangle(
            item.loc,
            self.patch_rectangle_2d,
            self.patch_rectangle_2d,
            rotations[item.state_type],
            picker=self.interact_pick_radius,
            zorder=1,
            lw=self.line_width_primary,
            transform=trans[item.state_type],
            **self.plot_properties["{}_ancilla_0".format(item.state_type)]
        )
        self.main_ax.add_artist(item.surface_plot)
        item.surface_plot.object = item

    def _plot_data(self, item):
        """Plots a circle representing a data-qubit."""
        item.surface_plot = plt.Circle(
            item.loc,
            self.patch_circle_2d,
            picker=self.interact_pick_radius,
            zorder=1,
            lw=self.line_width_primary,
            **self.plot_properties["data_qubit"]
        )
        self.main_ax.add_artist(item.surface_plot)
        item.surface_plot.object = item


class PerfectMeasurements(TemplateSimPM):
    """Plotting template code class for perfect measurements."""

    FigureClass = CodePlotPM

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.figure = None
        self.figure_destroyed = False

    def initialize(self, *args, **kwargs) -> None:
        super().initialize(*args, **kwargs)
        plot_properties = {}
        for error in self.errors.values():
            plot_properties.update(error.plot_properties)
        self.figure = self.FigureClass(self, plot_properties, **kwargs)

    def apply_errors(self, *args, z: float = 0, **kwargs):
        super().apply_errors(*args, z=z, **kwargs)
        self.plot_data("Errors applied", z=z, **kwargs)
        self.plot_ancilla("Ancilla-qubits measured", z=z, **kwargs)

    def plot_data(self, iter_name: Optional[str] = None, z: float = 0, **kwargs):
        for qubit in self.data_qubits[z].values():
            properties = {}
            for error in self.errors.values():
                names = error.get_draw_properties(qubit)
                for name in names:
                    if name not in properties:
                        properties.update(self.figure.plot_properties[name])
            if not properties:
                properties = self.figure.plot_properties["data_qubit"]
            self.figure.new_properties(qubit.surface_plot, properties)
        if iter_name:
            self.figure.draw_figure(new_iter_name=iter_name)

    def plot_ancilla(self, iter_name: Optional[str] = None, z: float = 0, **kwargs) -> None:
        for ancilla_qubit in self.ancilla_qubits[z].values():
            properties = self.figure.plot_properties[
                "{}_ancilla_{}".format(ancilla_qubit.state_type, int(ancilla_qubit.state))
            ]
            self.figure.new_properties(ancilla_qubit.surface_plot, properties)
        if iter_name:
            self.figure.draw_figure(new_iter_name=iter_name)
