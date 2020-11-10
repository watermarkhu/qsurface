from .sim import Toric as SimToric, Planar as SimPlanar
from .._template import Plot


class Toric(Plot, SimToric):
    """Plot MWPM decoder for the toric code.

    Parameters
    ----------
    args, kwargs
        Positional and keyword arguments are passed on to `.decoders._template.Plot` and `.decoders.mwpm.sim.Toric`.
    """

    pass


class Planar(Toric, SimPlanar):
    """Plot MWPM decoder for the planar code.

    Parameters
    ----------
    args, kwargs
        Positional and keyword arguments are passed on to `~.decoders.mwpm.plot.Toric` and `.decoders.mwpm.sim.Planar`.
    """

    pass
