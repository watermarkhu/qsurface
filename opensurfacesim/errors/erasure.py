from typing import Optional
from ._template import Sim as TemplateSim, Plot as TemplatePlot
import random


class Sim(TemplateSim):
    """Simulation erasure error class.

    Parameters
    ----------
    p_erasure : float or int, optional
        Default probability of erasure errors.
    """

    def __init__(self, *args, p_erasure: float = 0, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.default_error_rates = {"p_erasure": p_erasure}
        self.code.dataQubit.erasure = None
        self.code.ancillaQubit.erasure = None

    def random_error(self, qubit, p_erasure: Optional[float] = None, **kwargs):
        """Applies an erasure error.

        Parameters
        ----------
        qubit : DataQubit
            Qubit on which the error is (conditionally) applied.
        p_erasure : float or int, optional
            Overriding probability of erasure errors.

        See Also
        --------
        DataQubit
        """
        if p_erasure is None:
            p_erasure = self.default_error_rates["p_erasure"]

        if p_erasure != 0 and random.random() < p_erasure:
            self.erasure_error(qubit)

    def erasure_error(self, qubit):
        """Erases the `qubit` by resetting its attributes. """
        qubit.erasure = self.code.instance
        qubit._reset()


class Plot(TemplatePlot, Sim):
    """Plot erasure error class."""

    legend_params = {
        "legend_erasure": {
            "marker" : "$\u25CC$",
            "color" : "color_edge",
            "ms" : "legend_marker_size",
            "mfc" : "color_background",
            "mec" : "color_qubit_edge",
        }
    }
    legend_names = {"legend_erasure": "Erasure"}
    plot_params = {
        "qubit_erased": {
            "linestyle" : "line_style_tertiary",
            "facecolor" : "color_qubit_face"
        },
        "qubit_restored": {
            "linestyle" : "line_style_primary",
        }
    }

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, *kwargs)
        self.error_methods = {"erasure": self.erasure_error}

    def erasure_error(self, qubit):
        # Inherited docstrings
        super().erasure_error(qubit)
        self.code.figure.new_properties(qubit.surface_plot, self.code.figure.params.qubit_erased)
        properties = self.code.figure.params.qubit_restored
        future_properties = self.code.figure.future_dict[self.code.figure.history_iter + 3]
        if qubit.surface_plot in future_properties:
            future_properties[qubit.surface_plot].update(properties)
        else:
            future_properties[qubit.surface_plot] = properties
