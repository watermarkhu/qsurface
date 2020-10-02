from abc import abstractmethod
from typing import List, Tuple
from matplotlib.lines import Line2D
import matplotlib.pyplot as plt
from ...plot._template import Template2D as TemplatePlotPM
from .sim import PerfectMeasurements as TemplateSimPM, FaultyMeasurements as TemplateSimFM


class PerfectMeasurements(TemplateSimPM):
    """Plotting template code class for perfect measurements."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.figure = None
        self.figure_destroyed = False

    def apply_error(self, error_class, qubit, **kwargs):
        """Applies error to qubit and plots via error module."""
        error_class.apply_error(qubit, **kwargs)
        error_class.plot_error(self.figure, qubit, **kwargs)


class CodePlotPM(TemplatePlotPM):
    """Template surface code plot for perfect measurements.

    Parameters
    ----------
    code : `opensurfacesim.<code>.plot.PerfectMeasurements` class
        The `PerfectMeasurments` class from the `plot` module of any code, e.g. toric.
    """

    main_boundary = None
    legend_loc = (1, 1)

    def __init__(self, code: PerfectMeasurements, *args, **kwargs) -> None:
        self.code = code
        super().__init__(*args, **kwargs)

    def init_legend(self, legend_loc: Tuple[float, float], items: List[Line2D] = [], **kwargs) -> None:
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
            self._legend_circle("Qubit", mfc=self.color_qubit_face, mec=self.color_qubit_edge),
            self._legend_circle(
                "Vertex",
                ls="-",
                lw=self.line_width_primary,
                color=self.color_x_secundary,
                mfc=self.color_x_secundary,
                mec=self.color_x_secundary,
                marker="|",
            ),
            self._legend_circle(
                "Plaquette",
                ls="--",
                lw=self.line_width_primary,
                color=self.color_z_secundary,
                mfc=self.color_z_secundary,
                mec=self.color_z_secundary,
                marker="|",
            ),
        ]
        # Error legend items
        for error in self.code.errors.values():
            for name, attribute_names in error.legend_attributes.items():
                attributes = self.get_attributes(attribute_names, name=name)
                self.lh.append(self._legend_circle(name, **attributes))

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
        if self.code.pseudo_qubits:
            for item in self.code.pseudo_qubits[0].values():
                self._plot_ancilla(item)
        self.draw_figure()

    def parse_boundary_coordinates(self, *args: float) -> List[float]:
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
        item.surface_plot = {}
        for key, data in item.parity_qubits.items():
            line = Line2D(
                self.parse_boundary_coordinates(item.loc[0], data.loc[0]),
                self.parse_boundary_coordinates(item.loc[1], data.loc[1]),
                color=self.color_edge,
                lw=self.line_width_primary,
                ls=linestyles[item.state_type],
                zorder=0,
            )
            item.surface_plot[key] = line
            self.main_ax.add_artist(line)
            line.object = item

    def _plot_data(self, item):
        """Plots a circle representing a data-qubit."""
        item.surface_plot = plt.Circle(
            item.loc,
            self.scatter_size_2d,
            edgecolor=self.color_qubit_edge,
            facecolor=self.color_qubit_face,
            lw=self.line_width_primary,
            picker=self.interact_pick_radius,
            zorder=1,
        )
        self.main_ax.add_artist(item.surface_plot)
        item.surface_plot.object = item
