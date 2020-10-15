from .sim import Toric as ToricTemplate, Planar as PlanarTemplate
from .._template import PlotCode

class Toric(PlotCode, ToricTemplate):
    """Plot MWPM decoder for the toric code.
    
    Attributes
    ----------
    opposite_keys : dict
        Dictionary of opposite keys in `~.codes.elements.AncillaQubit`\ ``parity.qubits`` that aids plotting of matching edges. 
    """
    opposite_keys = dict(n="s", s="n", e="w", w="e")

class Planar(Toric, PlanarTemplate):
    """Plot MWPM decoder for the planar code."""
    pass