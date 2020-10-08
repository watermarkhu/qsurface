from typing import Optional
from ._template import Sim as TemplateSim, Plot as TemplatePlot
import random


class Sim(TemplateSim):
    """Erasure error class.

    Parameters
    ----------
    p_erasure : float or int, optional
        Default probability of erasure errors.
    """

    def __init__(self, *args, p_erasure: float = 0, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.default_error_rates = {"p_erasure": p_erasure}

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
        qubit.reset()


class Plot(TemplatePlot, Sim):

    legend_items = ["Erasure"]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, *kwargs)
        self.error_methods = {"erasure": self.erasure_error}


    def erasure_error(self, qubit):
        super().erasure_error(qubit)
        self.figure.new_properties(qubit.surface_plot, self.plot_properties["erased"])
        future_properties = self.plot_properties["non_erased"]
        future_objs = self.figure.future_dict[self.figure.history_iter + 2]

        if qubit.surface_plot in future_objs:
            future_objs[qubit.surface_plot].update(future_properties)
        else:
            future_objs[qubit.surface_plot] = future_properties

