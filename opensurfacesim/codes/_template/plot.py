from typing import List, Optional
from matplotlib.artist import Artist
from matplotlib.lines import Line2D
import matplotlib.pyplot as plt
from matplotlib.widgets import RadioButtons
from ...plot import Template2D as TemplatePlotPM, Template3D as TemplatePlotFM
from .sim import PerfectMeasurements as TemplateSimPM, FaultyMeasurements as TemplateSimFM
from ..elements import DataQubit, AncillaQubit


class PerfectMeasurements(TemplateSimPM):
    """Plotting template code class for perfect measurements.

    Attributes
    ----------
    figure : `~.codes._template.plot.PerfectMeasurements.Figure`
        Figure object of the current code.
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.figure = self.Figure(self, **kwargs)

    def initialize(self, *args, **kwargs):
        """Initializes the code with a figure. Also takes keyword arguments for `~.codes._template.plot.PerfectMeasurements.Figure.init_plot`.

        Since each error object delivers extra plot properties to the figure, which are dependent on the ``self.params`` values in the figure itself, we must initialize in the following sequence.

        - First load figure to load ``self.params`` instance of the `~.plot.PlotParams` dataclass.
        - Initialize lattice, error initialization must have figure properties
        - Draw figure with plot elements from errors
        """
        super().initialize(*args, **kwargs)
        self.figure.init_plot(**kwargs)
        self.figure.draw_figure("Initial")

    def _init_error(self, error_module, error_rates):
        """Initializes the ``error_module.Plot`` class of a error module."""
        error_type = error_module.__name__.split(".")[-1]
        self.errors[error_type] = error_module.Plot(self, **error_rates)

    def random_errors(self, *args, **kwargs):
        # Inherited docstrings
        super().random_errors(*args, **kwargs, measure=False)
        if self.figure.interactive:
            self.figure.interact_axes["error_buttons"].active = True
        self.plot_data("Errors applied", **kwargs)
        if self.figure.interactive:
            self.figure.interact_bodies["error_buttons"].set_active(0)
            self.figure.interact_axes["error_buttons"].active = False
        self.plot_ancilla("Ancilla-qubits measured", measure=True)

    def show_corrected(self, **kwargs):
        """Redraws the qubits and ancillas to show their states after decoding."""
        self.plot_data()
        self.plot_ancilla("Decoded", measure=True)

    def plot_data(self, iter_name: Optional[str] = None, **kwargs):
        """Update plots of all data-qubits. A plot iteration is added if a ``iter_name`` is supplied. See `~.plot.Template2D.draw_figure`."""

        for qubit in self.data_qubits[self.layer].values():
            self.figure._update_data(qubit, **kwargs)
        if iter_name:
            self.figure.draw_figure(new_iter_name=iter_name)

    def plot_ancilla(self, iter_name: Optional[str] = None, **kwargs):
        """Update plots of all ancilla-qubits. A plot iteration is added if a ``iter_name`` is supplied. See `~.plot.Template2D.draw_figure`."""
        for qubit in self.ancilla_qubits[self.layer].values():
            self.figure._update_ancilla(qubit, **kwargs)
        if iter_name:
            self.figure.draw_figure(new_iter_name=iter_name)

    class Figure(TemplatePlotPM):
        """Surface code plot for perfect measurements.

        The inner figure class that plots the surface code based on the ``Qubit.loc`` and ``Qubit.z`` values on the set of ``code.data_qubits``, ``code.ancilla_qubits`` and ``code.pseudo_qubits``. This allows for a high amount of code inheritance.

        An additional `matplotlib.widgets.RadioButtons` object is added to the figure which allows for the user to choose one of the loaded errors and apply the error directly to a qubit via `_pick_handler`.

        Parameters
        ----------
        code
            Surface code instance.
        kwargs
            Keyword arguments are passed on to `.plot.Template2D`.

        Attributes
        ----------
        error_methods : dict
            A dictionary of the various error methods loaded in the outer class.
        code_params
            Additional plotting parameters loaded to the `.plot.PlotParams` instance at ``self.params``.
        """

        code_params: dict = {
            "data00": {
                "facecolor": "color_qubit_face",
            },
            "data10": {
                "facecolor": "color_x_primary",
            },
            "data11": {
                "facecolor": "color_y_primary",
            },
            "data01": {
                "facecolor": "color_z_primary",
            },
            "xancilla0": {
                "facecolor": "color_qubit_face",
                "edgecolor": "color_qubit_edge",
            },
            "xancilla1": {
                "facecolor": "color_x_secondary",
                "edgecolor": "color_qubit_edge",
            },
            "zancilla0": {
                "facecolor": "color_qubit_face",
                "edgecolor": "color_qubit_edge",
            },
            "zancilla1": {
                "facecolor": "color_z_secondary",
                "edgecolor": "color_qubit_edge",
            },
        }

        def __init__(self, code: TemplateSimPM, *args, **kwargs) -> None:
            super().__init__(*args, **kwargs)
            self.code = code
            self.error_methods = {}
            self.params.load_params(self.code_params)

        def init_plot(self, **kwargs):
            """Plots all elements of the surface code onto the figure. Also takes keyword arguments for `~.codes._template.plot.PerfectMeasurements.Figure.init_legend`.

            An additional `matplotlib.widgets.RadioButtons` object is added to the figure which allows for the user to choose one of the loaded errors and apply the error directly to a qubit via `_pick_handler`. This object is added via the `init_plot` method to make sure that the errors are already loaded in ``self.code.errors``. The method for each loaded error is saved to ``self.error_methods``. See `.errors._template.Plot` for more information.
            """
            title = "{} code".format(str(self.code.__class__.__module__).split(".")[-2])
            self._init_axis(self.main_boundary, title=title, aspect="equal", **kwargs)
            self.init_legend(ncol=1, **kwargs)

            for error_module in self.code.errors.values():
                for error_name in error_module.gui_methods:
                    method = getattr(error_module, error_name)
                    self.error_methods[error_name] = method

            if self.interactive:
                self.interact_axes["error_buttons"] = plt.axes(self.params.axis_radio)
                self.interact_bodies["error_buttons"] = RadioButtons(
                    self.interact_axes["error_buttons"], ["info"] + list(self.error_methods.keys())
                )
                self.interact_axes["error_buttons"].active = False

            self._plot_surface()


        def init_legend(self, legend_items: List[Line2D] = [], **kwargs):
            """Initializes the legend of the main axis of the figure. Also takes keyword arguments for `~matplotlib.axes.Axes.legend`.

            The legend of the main axis ``self.main_ax`` consists of a series of `~matplotlib.line.Line2D` objects. The qubit, vertex and stars are always in the legend for a surface code plot. Any error from :doc:`../errors/index/` loaded in the code at ``code.errors`` in de outer class will add an extra element to the legend for differentiation if an error occurs. The `~matplotlib.line.Line2D` attributes are stored at ``error.Plot.legend_params`` of the error module (see `.errors._template.Plot`).

            Parameters
            ----------
            legend_items : list of `~matplotlib.lines.Line2D`, optional
                Additional elements to the legend.
            """
            # Main legend items
            self.lh = [
                self._legend_circle(
                    "Qubit [0,0]",
                    marker="o",
                    color=self.params.color_edge,
                    mec=self.params.color_qubit_edge,
                    mfc=self.params.color_qubit_face,
                    ms=self.params.legend_marker_size,
                ),
                self._legend_circle(
                    "Qubit [1,0]",
                    marker="o",
                    color=self.params.color_edge,
                    mec=self.params.color_qubit_edge,
                    mfc=self.params.color_x_primary,
                    ms=self.params.legend_marker_size,
                ),
                self._legend_circle(
                    "Qubit [0,1]",
                    marker="o",
                    color=self.params.color_edge,
                    mec=self.params.color_qubit_edge,
                    mfc=self.params.color_z_primary,
                    ms=self.params.legend_marker_size,
                ),
                self._legend_circle(
                    "Qubit [1,1]",
                    marker="o",
                    color=self.params.color_edge,
                    mec=self.params.color_qubit_edge,
                    mfc=self.params.color_y_primary,
                    ms=self.params.legend_marker_size,
                ),
            ]

            item_names = []
            # Error legend items
            for error in self.code.errors.values():
                for param_name, name in error.legend_titles.items():
                    if param_name not in item_names:
                        self.lh.append(self._legend_circle(name, **getattr(self.params, param_name)))
                        item_names.append(name)

            self.lh += [
                self._legend_scatter(
                    "Vertex",
                    facecolors=self.params.color_qubit_face,
                    edgecolors=self.params.color_qubit_edge,
                    linewidth=self.params.line_width_primary,
                    marker="s",
                ),
                self._legend_scatter(
                    "Star",
                    facecolors=self.params.color_qubit_face,
                    edgecolors=self.params.color_qubit_edge,
                    linewidth=self.params.line_width_primary,
                    marker="D",
                ),
            ]
            self.lh += legend_items
            labels = [artist.get_label() if hasattr(artist, "get_label") else artist[0].get_label() for artist in self.lh]
            self.legend_ax.legend(handles=self.lh, labels=labels, **kwargs.get("legend_kwargs", {}))

        def _pick_handler(self, event):
            """Function on when an object in the figure is picked

            If a specific error is selected, the error is applied via the selected error in ``self.error_methods``. The plot of the qubit is immediately updated.
            """
            selected = self.interact_bodies["error_buttons"].value_selected
            if selected == "info":
                print(event.artist.object)
            else:
                qubit = event.artist.object
                print(selected, qubit)
                self.error_methods[selected](qubit, instance=self.code.instance, temporary=True)

        def _plot_surface(self, z: float = 0, **kwargs):
            for qubit in self.code.data_qubits[z].values():
                self._plot_data(qubit, z=z)
            for qubit in self.code.ancilla_qubits[z].values():
                self._plot_ancilla(qubit, z=z)

        def _plot_ancilla(self, qubit: AncillaQubit, z: Optional[float] = None, **kwargs):
            """plots an ancilla-qubit.

            For an ancilla-qubit, a `matplotlib.patches.Rectangle` object is plotted. Based on the type of ancilla, the patch is rotated at a 45 degree angle. Additionally, a line is plotted towards each of the data-qubits in ``self.parity_qubits`` that represent the edges of the graph.

            Parameters
            ----------
            qubit : `~.codes.elements.AncillaQubit`
                Ancilla-qubit to plot.
            """

            linestyles = {
                "x": self.params.line_style_primary,
                "z": self.params.line_style_secondary,
            }
            rotations = {"x": 0, "z": 45}

            loc_parse = {
                "x": lambda x, y: (
                    x - self.params.patch_rectangle_2d / 2,
                    y - self.params.patch_rectangle_2d / 2,
                ),
                "z": lambda x, y: (x, y - self.params.patch_rectangle_2d * 2 ** (1 / 2) / 2),
            }

            # Plot graph edges
            qubit.surface_lines = {}
            for key, data in qubit.parity_qubits.items():
                line = self._draw_line(
                    self.code._parse_boundary_coordinates(self.code.size[0], qubit.loc[0], data.loc[0]),
                    self.code._parse_boundary_coordinates(self.code.size[1], qubit.loc[1], data.loc[1]),
                    ls=linestyles[qubit.state_type],
                    zorder=0,
                    lw=self.params.line_width_primary,
                    color=self.params.color_edge,
                    z=z,
                )
                qubit.surface_lines[key] = line
                line.object = qubit  # Save qubit to artist

            # Plot ancilla object
            rectangle = self._draw_rectangle(
                loc_parse[qubit.state_type](*qubit.loc),
                self.params.patch_rectangle_2d,
                self.params.patch_rectangle_2d,
                rotations[qubit.state_type],
                picker=self.params.blocking_pick_radius,
                zorder=1,
                lw=self.params.line_width_primary,
                z=z,
                **getattr(self.params, f"{qubit.state_type}ancilla0"),
            )
            qubit.surface_plot = rectangle
            rectangle.object = qubit  # Save qubit to artist

        def _update_ancilla(
            self,
            qubit: AncillaQubit,
            artist: Optional[Artist] = None,
            measure: bool = False,
            **kwargs,
        ):
            """Update properties of ancilla qubit plot.

            Parameters
            ----------
            qubit : `~.codes.elements.AncillaQubit`
                Ancilla-qubit to plot.
            """
            state = qubit.state if measure else qubit.measured_state

            properties = getattr(self.params, f"{qubit.state_type}ancilla{int(state)}")
            properties["edgecolor"] = (
                getattr(self.params, f"color_{qubit.state_type}_primary")
                if qubit.measurement_error
                else self.params.color_qubit_edge
            )
            if qubit.syndrome:
                properties.update(
                    {
                        "linestyle": self.params.line_style_primary,
                        "linewidth": self.params.line_width_secondary,
                    }
                )
            else:
                properties.update(
                    {
                        "linestyle": self.params.line_style_primary,
                        "linewidth": self.params.line_width_primary,
                    }
                )

            if not artist:
                artist = qubit.surface_plot
            self.new_properties(artist, properties)

        def _plot_data(self, qubit: DataQubit, z: Optional[float] = None, **kwargs):
            """Plots a circle representing a data-qubit.

            Parameters
            ----------
            qubit : `~.codes.elements.DataQubit`
                Data-qubit to plot.
            """
            x_state = int(qubit.edges["x"].state)
            z_state = int(qubit.edges["z"].state)
            properties = getattr(self.params, f"data{x_state}{z_state}")
            circle = self._draw_circle(
                qubit.loc,
                self.params.patch_circle_2d,
                picker=self.params.blocking_pick_radius,
                zorder=1,
                lw=self.params.line_width_primary,
                z=z,
                edgecolor=self.params.color_qubit_edge,
                **properties,
            )
            qubit.surface_plot = circle
            circle.object = qubit  # Save qubit to artist

        def _update_data(self, qubit: DataQubit, artist: Optional[Artist] = None, temporary=False, **kwargs):
            """Update properties of data qubit plot.

            Parameters
            ----------
            qubit : `~.codes.elements.DataQubit`
                Data-qubit to plot.
            temporary : bool, optional
                Makes update a temporary change.
            """
            x_state = int(qubit.edges["x"].state)
            z_state = int(qubit.edges["z"].state)
            properties = getattr(self.params, f"data{x_state}{z_state}")
            if not artist:
                artist = qubit.surface_plot
            if temporary:
                self.temporary_properties(artist, properties)
            else:
                self.new_properties(artist, properties)


class FaultyMeasurements(PerfectMeasurements, TemplateSimFM):
    """Plotting template code class for faulty measurements.

    Inherits from `.codes._template.sim.FaultyMeasurements` and `.codes._template.plot.PerfectMeasurements`. See documentation for these classes for more. 

    Dependent on the ``figure3d`` argument, either a 3D figure object is created that inherits from `~.plot.Template3D` and `.codes._template.plot.PerfectMeasurements.Figure`, or the 2D `.codes._template.plot.PerfectMeasurements.Figure` is used. 

    Parameters
    ----------
    args
        Positional arguments are passed on to `.codes._template.sim.FaultyMeasurements`. 
    figure3d
        Enables plotting on a 3D lattice. Disable to plot layer-by-layer on a 2D lattice, which increases responsiveness.
    kwargs
        Keyword arguments are passed on to `.codes._template.sim.FaultyMeasurements` and the figure object. 
    
    """
    def __init__(self, *args, figure3d: bool = True, **kwargs) -> None:
        self.figure3d = figure3d
        TemplateSimFM.__init__(self, *args, **kwargs)
        self.figure = self.Figure3D(self, **kwargs) if figure3d else self.Figure2D(self, **kwargs)

    def random_errors(self, **kwargs):
        # Inherited docstring
        TemplateSimFM.random_errors(self, **kwargs)

    def random_errors_layer(self, **kwargs):
        # Inherited docstring
        super().random_errors_layer(**kwargs)
        if self.figure.interactive:
            self.figure.interact_axes["error_buttons"].active = True
        self.plot_data(f"Layer {self.layer}: errors applied")

    def random_measure_layer(self, **kwargs):
        # Inherited docstring
        super().random_measure_layer(**kwargs)
        if self.figure.interactive:
            self.figure.interact_bodies["error_buttons"].set_active(0)
            self.figure.interact_axes["error_buttons"].active = False
        self.plot_ancilla(f"Layer {self.layer}: ancilla-qubits measured")

    def plot_data(self, iter_name: Optional[str] = None, **kwargs):
        """Update plots of all data-qubits in ``self.layer``. A plot iteration is added if a ``iter_name`` is supplied. See `.plot.Template2D.draw_figure`."""
        for qubit in self.data_qubits[self.layer].values():
            artist = qubit.surface_plot if self.figure3d else self.data_qubits[0][qubit.loc].surface_plot
            self.figure._update_data(qubit, artist, **kwargs)
        if iter_name:
            self.figure.draw_figure(new_iter_name=iter_name)

    def plot_ancilla(self, iter_name: Optional[str] = None, **kwargs):
        """Update plots of all ancilla-qubits in ``self.layer``. A plot iteration is added if a ``iter_name`` is supplied. See `.plot.Template2D.draw_figure`."""
        for qubit in self.ancilla_qubits[self.layer].values():
            artist = qubit.surface_plot if self.figure3d else self.ancilla_qubits[0][qubit.loc].surface_plot
            self.figure._update_ancilla(qubit, artist)
        if iter_name:
            self.figure.draw_figure(new_iter_name=iter_name)

    class Figure2D(PerfectMeasurements.Figure):
        def init_legend(self, legend_items: List[Line2D] = [], **kwargs):
            # Inherited docstring
            items = [
                self._legend_scatter(
                    "Syndrome vertex",
                    linestyle=self.params.line_style_primary,
                    linewidth=self.params.line_width_secondary,
                    facecolors=self.params.color_qubit_face,
                    edgecolors=self.params.color_qubit_edge,
                    marker="s",
                ),
                self._legend_scatter(
                    "Syndrome star",
                    linestyle=self.params.line_style_primary,
                    linewidth=self.params.line_width_secondary,
                    facecolors=self.params.color_qubit_face,
                    edgecolors=self.params.color_qubit_edge,
                    marker="D",
                ),
                self._legend_scatter(
                    "Faulty vertex",
                    facecolors=self.params.color_qubit_face,
                    edgecolors=self.params.color_x_primary,
                    linewidth=self.params.line_width_primary,
                    marker="s",
                ),
                self._legend_scatter(
                    "Faulty star",
                    facecolors=self.params.color_qubit_face,
                    edgecolors=self.params.color_z_primary,
                    linewidth=self.params.line_width_primary,
                    marker="D",
                ),
            ]
            super().init_legend(legend_items=items + legend_items, **kwargs)

        def _pick_handler(self, event):
            """Function on when an object in the figure is picked

            If a specific error is selected, the error is applied via the selected error in ``self.error_methods``. The plot of the qubit is immediately updated.
            """
            selected = self.interact_bodies["error_buttons"].value_selected
            if selected == "info":
                print(event.artist.object)
            else:
                plot_qubit = event.artist.object
                print(selected, plot_qubit)
                qubit = self.code.data_qubits[self.code.layer][plot_qubit.loc]
                self.error_methods[selected](qubit)
                self._update_data(qubit, artist=plot_qubit.surface_plot, temporary=True)

    class Figure3D(Figure2D, TemplatePlotFM):
        def _plot_surface(self):
            # Inherited docstring
            for z in range(self.code.layers):
                super()._plot_surface(z)
