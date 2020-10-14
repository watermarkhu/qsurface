from abc import ABC, abstractmethod
from ..configuration import get_attributes, init_config
import os
from matplotlib import pyplot as plt


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

    def __init__(self, code, **kwargs) -> None:
        self.code = code
        self.default_error_rates = {}
        self.type = str(self.__module__).split(".")[-1]

    def __repr__(self) -> str:
        return "{} error object with defaults: {}".format(self.type, self.default_error_rates)

    @abstractmethod
    def random_error(self, qubit, **kwargs) -> None:
        """Applies the current error type to the `qubit`.

        Parameters
        ----------
        qubit : DataQubit
            Qubit on which the error is (conditionally) applied.
        """
        pass


class Plot(Sim):
    """Template plot class for errors.

    Parameters
    ----------
    code : `~.decoders._template.PlotCode`
        Plotting surface code class. 

    Attributes
    ----------
    legend_items : list
        The legend items in 'plot_legend_errors.ini' to include if this error is loaded.
    error_methods : dict
        Dictionary of error methods. Used by :meth:`opensurfacesim.code._template.plot.PerfectMeasurements.Figure._pickhandler` to apply the error directly on the figure. Each method must be of the following form.

            def error_method(qubit, rate=0):
                pass

    plot_properties : dict of dict
        Dictionary of plot properties for each specific error class, defined in 'plot_errors.ini'.
    legend_properties : dict of dict
        Dictionary of `matplotlib.lines.Line2D` properties for each legend item, defined in 'plot_errors_legend.ini'.
    """

    legend_items = []

    def __init__(self, code, *args, **kwargs) -> None:
        super().__init__(code, *args, *kwargs)
        self.error_methods = {}
        self.plot_properties = get_attributes(
            self.code.figure.rc, init_config(os.path.dirname(os.path.abspath(__file__)) + "/plot_errors.ini")
        )
        self.legend_properties = get_attributes(
            self.code.figure.rc,
            init_config(os.path.dirname(os.path.abspath(__file__)) + "/plot_errors_legend.ini"),
        )

    def _get_legend_properties(self):
        """Returns the dictionary of properties for `matplotlib.lines.Line2D` of the errors in the current class."""
        return {key: self.legend_properties[key] for key in self.legend_items}
