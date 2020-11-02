from .sim import Toric as SimToric, Planar as SimPlanar
from .._template import PlotCode


class Toric(PlotCode, SimToric):
    """Plot MWPM decoder for the toric code.

    Attributes
    ----------
    opposite_keys : dict
        Dictionary of opposite keys in `~.codes.elements.AncillaQubit`\ ``parity.qubits`` that aids plotting of matching edges.
    """

    opposite_keys = dict(n="s", s="n", e="w", w="e")


class Planar(Toric, SimPlanar):
    """Plot MWPM decoder for the planar code."""

    pass
