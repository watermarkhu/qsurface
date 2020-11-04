from __future__ import annotations
from abc import ABC, abstractmethod
from ..codes.elements import Qubit
from matplotlib import pyplot as plt
from functools import wraps


class Sim(ABC):
    """Template simulation class for errors.

    The template simulation error class can be used as a parent class for error modules for surface code classes that inherit from `.codes._template.sim.PerfectMeasurements` or `.codes._template.sim.FaultyMeasurements`. The error of the module must be applied to each qubit separately using the abstract method `random_error`. 

    Parameters
    ----------
    code : `.codes._template.sim.PerfectMeasurements`
        Simulation surface code class.

    Attributes
    ----------
    default_error_rates : dict of float
        The error rates that are applied at default.
    """

    def __init__(self, code=None, **kwargs) -> None:
        self.code = code
        self.default_error_rates = {}
        self.type = str(self.__module__).split(".")[-1]

    def __repr__(self) -> str:
        return "{} error object with defaults: {}".format(self.type, self.default_error_rates)

    @abstractmethod
    def random_error(self, qubit: Qubit, **kwargs) -> None:
        """Applies the current error type to the `qubit`.

        Parameters
        ----------
        qubit : DataQubit
            Qubit on which the error is (conditionally) applied.
        """
        pass


class Plot(Sim):
    """Template plot class for errors.

    The template plotting error class can be used as a parent class for error modules for surface code classes that inherit from `.codes._template.plot.PerfectMeasurements` or `.codes._template.plot.FaultyMeasurements`, which have a figure object attribute at ``code.figure``. The error of the module must be applied to each qubit separately using the abstract method `random_error`. 

    To change properties of the qubit (a `matplotlib.patches.Circle` object) if an error has been appied to visualize the error. The template plot error class features an easy way to define the plot properties of an error. First of all, each error must be defined in an *error method* that applies the error to the qubit. The template can contain multiple *error methods*, all of which must be called by `random_error`. For all errors that we wish to plot, we must add the names of the methods to ``self.error_methods``. The plot properties are stored under the same name in ``self.plot_params``. 

    .. code-block:: python

        class CustomPlotError(Plot):

            error_methods = ["example_method"]
            plot_params = {
                "example_method": {"edgecolor": "color_edge", "facecolor": (0,0,0,0)}
            }

            def random_error(self, qubit):
                if random.random < 0.5:
                    self.error_method(qubit)
            
            def example_method(self, qubit):
                # apply error
                pass

    Note that the properties can either be literal or refer to some attribute of the `~.plot.PlotParams` object stored at ``self.code.figure.params`` (see `~.plot.PlotParams.load_params`). Thus the name for the error methods **must be unique** to any attribute in `~plot.PlotParams`.
    
    Similarly, additional legend items can be added to the surface code plot ``self.code.figure``. Each legend item is a ``matplotlib.lines.line2D``. The properties for each additional item in the legend is stored at ``self.legend_params``, and must also be unique to any `~.plot.PlotParams` attribute. The legend titles for each item is stored in ``self.legend_titles`` at the same keys. The additional legend items are added in `~.codes._template.PerfectMeasurements.Figure.init_legend`. 

    .. code-block:: python

        class CustomPlotError(Plot):

            error_methods = ["example_method"]
            plot_params = {
                "example_method": {"edgecolor": "color_edge", "facecolor": (0,0,0,0)}
            }
            legend_params = {
                "example_item": {
                    "marker": "o",
                    "color": "color_edge",
                    "mfc": (1, 0, 0),
                    "mec": "g",
                },
            }
            legend_titles = {
                "example_item": "Example error"
            }

            def random_error(self, qubit):
                if random.random < 0.5:
                    self.error_method(qubit)
            
            def example_method(self, qubit):
                # apply error
                pass

    Finally, error methods can be also be added to the GUI of the surface code plot. For this, each error method must a *static method* that is not dependant on the error class. Each error method to be added in the GUI must be included in ``self.gui_methods``. The GUI elements are included in `~.codes._template.PerfectMeasurements.Figure.init_plot`. 

    .. code-block:: python

        class CustomPlotError(Plot):

            error_methods = ["example_method"]
            gui_methods = ["example_method"]
            plot_params = {
                "example_method": {"edgecolor": "color_edge", "facecolor": (0,0,0,0)}
            }
            legend_params = {
                "example_item": {
                    "marker": "o",
                    "color": "color_edge",
                    "mfc": (1, 0, 0),
                    "mec": "g",
                },
            }
            legend_titles = {
                "example_item": "Example error"
            }

            def random_error(self, qubit):
                if random.random < 0.5:
                    self.error_method(qubit)
            
            @staticmethod
            def example_method(qubit):
                # apply error
                pass

    Parameters
    ----------
    code : `~.codes._template.plot.PerfectMeasurements`
        Plotting surface code class.

    Attributes
    ----------
    error_methods : list
        List of names of the error methods that changes the qubit surface code plot according to properties defined in ``self.plot_params``. 
    plot_params : {method_name: properties}
        Qubit plot properties to apply for each of the error methods in ``self.error_methods``. Properties are loaded to the `~.plot.PlotParams` object stored at the ``self.code.figure.params`` attribute of the surface code plot (see `~.plot.PlotParams.load_params`). 
    legend_params {method_name: Line2D properties}
        Legend items to add to the surface code plot. Properties are loaded to the `~.plot.PlotParams` object stored at the ``self.code.figure.params`` attribute of the surface code plot (see `~.plot.PlotParams.load_params`), and used to initialize a `~matplotlib.lines.Line2D` legend item. 
    legend_titles : {method_name: legend_title}
        Titles to display for the legend items in ``self.legend_params``.
    gui_permanent : bool
        If enabled, the application of an error method on a qubit cannot be reversed within the same simulation instance.
    gui_methods : list
        List of names of the static error methods include in the surface plot GUI. 
    """
    error_methods: list = []
    legend_params: dict = {}
    legend_titles: dict = {}
    plot_params: dict = {}
    gui_permanent: bool = False
    gui_methods: list = []
    

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, *kwargs)

        figure = self.code.figure
        figure.params.load_params(self.legend_params)
        figure.params.load_params(self.plot_params)

        for error_name in self.error_methods:
            setattr(self, error_name, self.plot_error(error_name))

    def plot_error(self, error_name):
        """Decorates the error method with plotting features. 

        The method ``error_name`` is decorated with plot property changes defined in ``self.plot_params``. For each of the properties to change, the original property value of the artist is stored and requested as a change at the end of the simulation instance. 

        See Also
        --------
        `.plot.Template2D.temporary_properties`
        `.plot.Template2D.new_properties`. 
        """
        sim_method = getattr(self, error_name)
        figure = self.code.figure

        @wraps(sim_method)
        def wrapped_method(qubit: Qubit, temporary: bool = False, **kwargs):
            output = sim_method(qubit, **kwargs)

            qubit.errors[error_name] = 0 if qubit.errors[error_name] else self.code.instance
            artist = qubit.surface_plot
            properties = getattr(figure.params, error_name)

            if artist in figure.temporary_saved:
                restored_properties = {
                    prop: figure.temporary_saved[artist].get(prop, plt.getp(artist, prop)) for prop in properties
                }
            else:
                restored_properties = {prop: plt.getp(artist, prop) for prop in properties}

            future_properties = figure.future_dict[figure.history_iter + 3]

            if temporary:
                if self.gui_permanent or qubit.errors[error_name] == self.code.instance:
                    figure.temporary_properties(artist, properties)
                    if artist in future_properties:
                        future_properties[artist].update(restored_properties)
                    else:
                        future_properties[artist] = restored_properties
                else:
                    restored_properties = {
                        prop: figure.temporary_saved[artist].get(prop)
                        for prop in properties
                        if prop in figure.temporary_saved[artist]
                    }
                    figure.temporary_properties(artist, restored_properties)
            else:
                figure.new_properties(artist, properties)
                if artist in future_properties:
                    future_properties[artist].update(restored_properties)
                else:
                    future_properties[artist] = restored_properties

            return output

        return wrapped_method
