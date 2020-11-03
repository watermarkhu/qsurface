from __future__ import annotations
from abc import ABC, abstractmethod
from ..codes.elements import Qubit
from matplotlib import pyplot as plt
from functools import wraps


class Sim(ABC):
    """Template simulation class for errors.

    Parameters
    ----------
    code : `~.decoders._template.SimCode`
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

    .. todo:: This documentation is out of date

    Parameters
    ----------
    code : `~.decoders._template.PlotCode`
        Plotting surface code class.

    Attributes
    ----------
    legend_params, plot_params
        Additional plotting parameters loaded to the `.plot.PlotParams` instance at ``self.params``.
    legend_names : dict
        Titles to display for the legend items in ``legend_params``.
    error_methods : dict
        Dictionary of error methods. Used by :meth:`opensurfacesim.code._template.plot.PerfectMeasurements.Figure._pickhandler` to apply the error directly on the figure. Each method must be of the following form.

            def error_method(qubit, rate=0):
                pass

    plot_properties : dict of dict
        Dictionary of plot properties for each specific error class, defined in 'plot_errors.ini'.
    legend_properties : dict of dict
        Dictionary of `matplotlib.lines.Line2D` properties for each legend item, defined in 'plot_errors_legend.ini'.
    """

    permanent_on_click = False
    error_methods = []
    legend_params = {}
    legend_names = {}
    plot_params = {}

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, *kwargs)

        figure = self.code.figure
        figure.params.load_params(self.legend_params)
        figure.params.load_params(self.plot_params)

        for error_name in self.error_methods:
            setattr(self, error_name, self.plot_error(error_name))

    def plot_error(self, error_name):
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
                if self.permanent_on_click or qubit.errors[error_name] == self.code.instance:
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
