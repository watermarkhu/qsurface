from ..codes.elements import Qubit
from ._template import Sim as TemplateSim, Plot as TemplatePlot
from typing import Optional
import random


class Sim(TemplateSim):
    """Simulation Pauli error class.

    Parameters
    ----------
    p_bitflip : float or int, optional
        Default probability of X-errors or bitflip errors.
    p_phaseflip : float or int, optional
        Default probability of Z-errors or phaseflip errors.
    """

    def __init__(self, *args, p_bitflip: float = 0, p_phaseflip: float = 0, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.default_error_rates = {"p_bitflip": p_bitflip, "p_phaseflip": p_phaseflip}

    def random_error(self, qubit: Qubit, p_bitflip: float = 0, p_phaseflip: float = 0, **kwargs):
        """Applies a Pauli error, bitflip and/or phaseflip.

        Parameters
        ----------
        qubit
            Qubit on which the error is (conditionally) applied.
        p_bitflip
            Overriding probability of X-errors or bitflip errors.
        p_phaseflip
            Overriding probability of Z-errors or phaseflip errors.

        """
        if p_bitflip is None:
            p_bitflip = self.default_error_rates["p_bitflip"]
        if p_phaseflip is None:
            p_phaseflip = self.default_error_rates["p_phaseflip"]

        do_bitflip = p_bitflip != 0 and random.random() < p_bitflip
        do_phaseflip = p_phaseflip != 0 and random.random() < p_phaseflip

        if do_bitflip and do_phaseflip:
            self.bitphaseflip(qubit)
        elif do_bitflip:
            self.bitflip(qubit)
        elif do_phaseflip:
            self.phaseflip(qubit)

    @staticmethod
    def bitflip(qubit: Qubit, **kwargs):
        """Applies a bitflip or Pauli X on ``qubit``."""
        qubit.edges["x"].state = not qubit.edges["x"].state

    @staticmethod
    def phaseflip(qubit: Qubit, **kwargs):
        """Applies a phaseflip or Pauli Z on ``qubit``."""
        qubit.edges["z"].state = not qubit.edges["z"].state

    @staticmethod
    def bitphaseflip(qubit: Qubit, **kwargs):
        """Applies a bitflip and phaseflip or ZX on ``qubit``."""
        qubit.edges["x"].state = not qubit.edges["x"].state
        qubit.edges["z"].state = not qubit.edges["z"].state


class Plot(TemplatePlot, Sim):
    """Plot Pauli error class."""

    permanent_on_click = False

    error_methods = ["bitflip", "phaseflip", "bitphaseflip"]
    gui_methods = ["bitflip", "phaseflip"]

    legend_params = {
        "legend_bitflip": {
            "marker": "o",
            "color": "color_edge",
            "ms": "legend_marker_size",
            "mfc": "color_qubit_face",
            "mec": "color_x_primary",
        },
        "legend_phaseflip": {
            "marker": "o",
            "color": "color_edge",
            "ms": "legend_marker_size",
            "mfc": "color_qubit_face",
            "mec": "color_y_primary",
        },
        "legend_bitphaseflip": {
            "marker": "o",
            "color": "color_edge",
            "ms": "legend_marker_size",
            "mfc": "color_qubit_face",
            "mec": "color_z_primary",
        },
    }
    legend_titles = {
        "legend_bitflip": "X flip",
        "legend_phaseflip": "Z flip",
        "legend_bitphaseflip": "Y flip",
    }

    plot_params = {
        "bitflip": {"edgecolor": "color_x_primary"},
        "phaseflip": {"edgecolor": "color_z_primary"},
        "bitphaseflip": {"edgecolor": "color_y_primary"},
    }
