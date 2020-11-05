from ._template import Sim as TemplateSim, Plot as TemplatePlot
from ..codes.elements import DataQubit
from typing import Optional, Tuple
import random


class Sim(TemplateSim):
    """Simulation erasure error class.

    Parameters
    ----------
    p_erasure
        Default probability of erasure errors.
    initial_states
        Default state of the qubit after re-initialization. 
    """

    def __init__(self, *args, p_erasure: float = 0, initial_states: Tuple[float, float] = (0, 0), **kwargs):
        super().__init__(*args, **kwargs)
        self.initial_states = initial_states
        self.default_error_rates = {"p_erasure": p_erasure}
        self.code._DataQubit.erasure = None
        self.code._AncillaQubit.erasure = None
        # TODO above line is required for unionfind/ufns decoder, but doesn't make sense

    def random_error(self, qubit, p_erasure: float = 0, initial_states: Optional[Tuple[float, float]] = None, **kwargs):
        """Applies an erasure error.

        Parameters
        ----------
        qubit
            Qubit on which the error is (conditionally) applied.
        p_erasure
            Overriding probability of erasure errors.
        initial_states
            Overriding state of the qubit after re-initialization. 
        """
        if p_erasure is None:
            p_erasure = self.default_error_rates["p_erasure"]
        if p_erasure != 0 and random.random() < p_erasure:
            if initial_states is None:
                initial_states = self.initial_states
            self.erasure(qubit, instance=getattr(self.code, "instance", 0), initial_states=initial_states, **kwargs)

    @staticmethod
    def erasure(qubit: DataQubit, instance: float = 0, initial_states: Tuple[float, float] = (0, 0), **kwargs):
        """Erases the ``qubit`` by resetting its attributes.
        
        Parameters
        ----------
        qubit
            Qubit to erase. 
        instance
            Current simulation instance. 
        initial_states
            State of the qubit after re-initialization.
        """
        qubit.erasure = instance
        qubit._reinitialize(initial_states=initial_states, **kwargs)


class Plot(TemplatePlot, Sim):
    """Plot erasure error class."""

    permanent_on_click = True

    error_methods = ["erasure"]
    gui_methods = ["erasure"]

    legend_params = {
        "legend_erasure": {
            "marker": "$\u25CC$",
            "color": "color_edge",
            "ms": "legend_marker_size",
            "mfc": "color_background",
            "mec": "color_qubit_edge",
        }
    }

    legend_titles = {"legend_erasure": "Erasure"}

    plot_params = {"erasure": {"linestyle": "line_style_tertiary"}}
