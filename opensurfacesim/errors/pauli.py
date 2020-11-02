from ..codes.elements import Qubit
from typing import Optional
from ._template import Sim as TemplateSim, Plot as TemplatePlot
import random


class Sim(TemplateSim):
    """Simulation Pauli error class.

    Parameters
    ----------
    p_bitflip : float or int, optional
        Default probability of X-errors or bit-flip errors.
    p_phaseflip : float or int, optional
        Default probability of Z-errors or phase-flip errors.
    """

    def __init__(self, *args, p_bitflip: float = 0, p_phaseflip: float = 0, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.default_error_rates = {"p_bitflip": p_bitflip, "p_phaseflip": p_phaseflip}

    def random_error(self, qubit: Qubit, p_bitflip: Optional[float] = None, p_phaseflip: Optional[float] = None, **kwargs):
        """Applies a Pauli error, bit-flip and/or phase-flip.

        Parameters
        ----------
        p_bitflip : float or int, optional
            Overriding probability of X-errors or bit-flip errors.
        p_phaseflip : float or int, optional
            Overriding probability of Z-errors or phase-flip errors.

        See Also
        --------
        DataQubit
        """
        if p_bitflip is None:
            p_bitflip = self.default_error_rates["p_bitflip"]
        if p_phaseflip is None:
            p_phaseflip = self.default_error_rates["p_phaseflip"]

        if p_bitflip != 0 and random.random() < p_bitflip:
            self.bitflip_error(qubit)
        if p_phaseflip != 0 and random.random() < p_phaseflip:
            self.phaseflip_error(qubit)

    def bitflip_error(self, qubit):
        """Applies a bitflip or Pauli X on ``qubit``."""
        qubit.edges["x"].state = not qubit.edges["x"].state

    def phaseflip_error(self, qubit):
        """Applies a phaseflip or Pauli Z on ``qubit``."""
        qubit.edges["z"].state = not qubit.edges["z"].state


class Plot(TemplatePlot, Sim):
    """Plot Pauli error class."""

    legend_params = {
        "legend_bitflip": {
            "marker": "o",
            "color": "color_edge",
            "ms": "legend_marker_size",
            "mfc": "color_x_primary",
            "mec": "color_x_primary",
        },
        "legend_phaseflip": {
            "marker": "o",
            "color": "color_edge",
            "ms": "legend_marker_size",
            "mfc": "color_y_primary",
            "mec": "color_y_primary",
        },
        "legend_bitphaseflip": {
            "marker": "o",
            "color": "color_edge",
            "ms": "legend_marker_size",
            "mfc": "color_z_primary",
            "mec": "color_z_primary",
        },
    }
    legend_names = {
        "legend_bitflip": "X flip",
        "legend_phaseflip": "Z flip",
        "legend_bitphaseflip": "Y flip",
    }

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, *kwargs)
        self.error_methods = {"bitflip": self.bitflip_error, "phaseflip": self.phaseflip_error}
