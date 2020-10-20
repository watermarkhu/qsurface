from typing import List, Optional, Tuple
from pathlib import Path
from matplotlib.lines import Line2D
from matplotlib.patches import Circle, Rectangle
import matplotlib.pyplot as plt
from matplotlib.widgets import RadioButtons
from ...configuration import get_attributes, init_config
from ...plot import Template2D as TemplatePlotPM
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
        
        Since each error object delivers extra plot properties to the figure, which are dependent on the ``self.rc`` values in the figure itself, we must initialize in the following sequence. 

        - First load figure to get ``self.rc`` properties
        - Initialize lattice, error initialization must have figure properties
        - Draw figure with plot elements from errors
        """
        super().initialize(*args, **kwargs)
        self.figure.init_plot(**kwargs)

    def _init_error(self, error_module, error_rates):
        """Initializes the ``error_module.Plot`` class of a error module."""
        error_type = error_module.__name__.split(".")[-1]
        self.errors[error_type] = error_module.Plot(self, **error_rates)

    def random_errors(self, *args, z: float = 0, **kwargs):
        # Inherited docstrings
        super().random_errors(*args, z=z, **kwargs)
        self.figure.interact_axes["error_buttons"].active = True
        self.plot_data("Errors applied", z=z, **kwargs)
        self.figure.interact_bodies["error_buttons"].set_active(0)
        self.figure.interact_axes["error_buttons"].active = False
        self.plot_ancilla("Ancilla-qubits measured", z=z, **kwargs)
    
    def show_corrected(self, **kwargs):
        self.plot_data()
        self.plot_ancilla("Decoded.")

    def plot_data(self, iter_name: Optional[str] = None, z: float = 0, **kwargs):
        """Update plots of all data-qubits in layer ``z``. A plot iteration is added if a ``iter_name`` is supplied. See `.plot.Template2D.draw_figure`."""
        for qubit in self.data_qubits[z].values():
            self.figure._update_data(qubit)
        if iter_name:
            self.figure.draw_figure(new_iter_name=iter_name)

    def plot_ancilla(self, iter_name: Optional[str] = None, z: float = 0, **kwargs):
        """Update plots of all ancilla-qubits in layer ``z``. A plot iteration is added if a ``iter_name`` is supplied. See `.plot.Template2D.draw_figure`."""
        for qubit in self.ancilla_qubits[z].values():
            self.figure._update_ancilla(qubit)
        if iter_name:
            self.figure.draw_figure(new_iter_name=iter_name)


    class Figure(TemplatePlotPM):
        """Template surface code plot for perfect measurements.

        The inner figure class that plots the surface code based on the ``Qubit.loc`` and ``Qubit.z`` values on the set of ``code.data_qubits``, ``code.ancilla_qubits`` and ``code.pseudo_qubits``. This allows for a high amount of code inheritance. 

        An additional `matplotlib.widgets.RadioButtons` object is added to the figure which allows for the user to choose one of the loaded errors and apply the error directly to a qubit via `_pick_handler`. 

        Default values for code-plot properties such as colors and linewidths are saved in a *plot_codes.ini* file. All parameters within the ini file are parsed by `~.configuration.read_config` and saved to the ``self.rc`` dictionary. The values defined in the ini file can be the predefined values in *plot.ini*. 

        Parameters
        ----------
        code : `~codes._template.plot.PerfectMeasurements`

        Attributes
        ----------
        error_methods : dict
            A dictionary of the various error methods loaded in the outer class. 
        """

        main_boundary = None

        def __init__(self, code: TemplateSimPM, *args, **kwargs) -> None:
            super().__init__(*args, init_plot=False, **kwargs)
            self.code = code
            self.error_methods = {}
            self.rc.update(
                get_attributes(
                    self.rc,
                    init_config(
                        Path(__file__).resolve().parent.parent / "plot_codes.ini"
                    )
                )
            )

        def init_plot(self, **kwargs):
            """Plots all elements of the surface code onto the figure. Also takes keyword arguments for `~.codes._template.plot.PerfectMeasurements.Figure.init_legend`. 

            An additional `matplotlib.widgets.RadioButtons` object is added to the figure which allows for the user to choose one of the loaded errors and apply the error directly to a qubit via `_pick_handler`. This object is added via the `init_plot` method to make sure that the errors are already loaded in `self.code.errors`. The method for each loaded error is saved to `self.error_methods`. 
            """
            title = "{} lattice".format(str(self.code.__class__.__module__).split(".")[-2])
            self._init_axis(self.main_boundary, title=title, **kwargs)
            self.init_legend(ncol=1, **kwargs)

            for error_module in self.code.errors.values():
                for name, method in error_module.error_methods.items():
                    self.error_methods[name] = method
            self.interact_axes["error_buttons"] = plt.axes(self.rc["axis_radio"])
            self.interact_bodies["error_buttons"] = RadioButtons(
                self.interact_axes["error_buttons"], ["info"] + list(self.error_methods.keys())
            )
            self.interact_axes["error_buttons"].active = False

            for qubit in self.code.data_qubits[0].values():
                self._plot_data(qubit)
            for qubit in self.code.ancilla_qubits[0].values():
                self._plot_ancilla(qubit)
            self.draw_figure()

        def init_legend(self, legend_items: List[Line2D] = [], **kwargs):
            """Initializes the legend of the main axis of the figure. Also takes keyword arguments for `~matplotlib.axes.Axes.legend`. 

            The legend of the main axis ``self.main_ax`` consists of a series of `~matplotlib.line.Line2D` objects. The qubit, vertex and stars are always in the legend for a surface code plot. Any error from :doc:`../errors/index/` loaded in the code at ``code.errors`` in de outer class will add an extra element to the legend for differentiation if an error occurs. The 'Line2D' attributes are stored at ``error.Plot.legend_properties`` of the error module. 

            Parameters
            ----------
            legend_items : list of `~matplotlib.lines.Line2D`, optional
                Additional elements to the legend.
            """
            # Main legend items
            self.lh = [
                self._legend_circle(
                    "Qubit",
                    marker="o",
                    color=self.rc["color_edge"],                  
                    mec=self.rc["color_qubit_edge"],
                    mfc=self.rc["color_qubit_face"],
                    ms=self.rc["legend_marker_size"],
                )
            ]
            item_names = []
            # Error legend items
            for error in self.code.errors.values():
                for name, properties in error._get_legend_properties().items():
                    if name not in item_names:
                        self.lh.append(self._legend_circle(name, **properties))
                        item_names.append(name)

            self.lh += [
                self._legend_circle(
                    "Vertex",
                    ls="-",
                    color=self.rc["color_edge"],
                    mfc=self.rc["color_qubit_face"],
                    mec=self.rc["color_qubit_edge"],
                    marker="s",
                    ms=5,
                ),
                self._legend_circle(
                    "Star",
                    ls="--",
                    color=self.rc["color_edge"],
                    mfc=self.rc["color_qubit_face"],
                    mec=self.rc["color_qubit_edge"],
                    marker="D",
                    ms=5,
                ),
            ]
            self.lh += legend_items
            self.legend_ax.legend(handles=self.lh, **kwargs)

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
                self.error_methods[selected](qubit)
                self._update_data(qubit, temporary=True)

        def _plot_ancilla(self, qubit: AncillaQubit):
            """plots an ancilla-qubit.

            For an ancilla-qubit, a `matplotlib.patches.Rectangle` object is plotted. Based on the type of ancilla, the patch is rotated at a 45 degree angle. Additionally, a line is plotted towards each of the data-qubits in ``self.parity_qubits`` that represent the edges of the graph.

            Parameters
            ----------
            qubit : `~.codes.elements.AncillaQubit`
                Ancilla-qubit to plot.
            """
            linestyles = {"x": self.rc["line_style_primary"], "z": self.rc["line_style_secondary"]}
            rotations = {"x": 0, "z": 45}

            loc_parse = {
                "x": lambda x, y: (x - self.rc["patch_rectangle_2d"] / 2, y - self.rc["patch_rectangle_2d"] / 2),
                "z": lambda x, y: (x, y - self.rc["patch_rectangle_2d"] * 2 ** (1 / 2) / 2),
            }

            # Plot graph edges
            qubit.surface_lines = {}
            for key, data in qubit.parity_qubits.items():
                line = Line2D(
                    self.code._parse_boundary_coordinates(self.code.size[0], qubit.loc[0], data.loc[0]),
                    self.code._parse_boundary_coordinates(self.code.size[1], qubit.loc[1], data.loc[1]),
                    ls=linestyles[qubit.state_type],
                    zorder=0,
                    lw=self.rc["line_width_primary"],
                    color=self.rc["color_edge"],
                )
                qubit.surface_lines[key] = line
                self.main_ax.add_artist(line)
                line.object = qubit                                 # Save qubit to artist
            
            # Plot ancilla object
            qubit.surface_plot = Rectangle(
                loc_parse[qubit.state_type](*qubit.loc),
                self.rc["patch_rectangle_2d"],
                self.rc["patch_rectangle_2d"],
                rotations[qubit.state_type],
                picker=self.rc["interact_pick_radius"],
                zorder=1,
                lw=self.rc["line_width_primary"],
                **self.rc["{}ancilla0".format(qubit.state_type)]
            )
            self.main_ax.add_artist(qubit.surface_plot)
            qubit.surface_plot.object = qubit                       # Save qubit to artist

        def _update_ancilla(self, qubit : AncillaQubit, temporary=False):
            """Update properties of ancilla qubit plot.

            Parameters
            ----------
            qubit : `~.codes.elements.AncillaQubit`
                Ancilla-qubit to plot.
            temporary : bool, optional
                Makes update a temporary change. 
            """
            properties = self.rc[
                "{}ancilla{}".format(qubit.state_type, int(qubit.state))
            ]
            self.new_properties(qubit.surface_plot, properties)


        def _plot_data(self, qubit: DataQubit):
            """Plots a circle representing a data-qubit.
            
            Parameters
            ----------
            qubit : `~.codes.elements.DataQubit`
                Data-qubit to plot.
            """
            qubit.surface_plot = Circle(
                qubit.loc,
                self.rc["patch_circle_2d"],
                picker=self.rc["interact_pick_radius"],
                zorder=1,
                lw=self.rc["line_width_primary"],
                **self.rc["data00"]
            )
            self.main_ax.add_artist(qubit.surface_plot)
            qubit.surface_plot.object = qubit                       # Save qubit to artist

        def _update_data(self, qubit : DataQubit, temporary=False):
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
            properties = self.rc["data{}{}".format(x_state, z_state)]
            if temporary:
                self.temporary_properties(qubit.surface_plot, properties)
            else:
                self.new_properties(qubit.surface_plot, properties)


