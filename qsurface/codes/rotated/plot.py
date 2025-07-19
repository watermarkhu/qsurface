from .sim import PerfectMeasurements as SimPM, FaultyMeasurements as SimFM
from .._template.plot import PerfectMeasurements as TemplatePM, FaultyMeasurements as TemplateFM


class PerfectMeasurements(SimPM, TemplatePM):
    # Inherited docstring

    class Figure(TemplatePM.Figure):
        # Inherited docstring

        def __init__(self, code, *args, **kwargs) -> None:
            self.main_boundary = [-1, -1, code.size[0] + 1, code.size[1] + 1]
            super().__init__(code, *args, **kwargs)


class FaultyMeasurements(SimFM, TemplateFM):
    """Plotting code class for faulty measurements.

    Inherits from `.codes.planar.sim.FaultyMeasurements` and `.codes.planar.plot.PerfectMeasurements`. See documentation for these classes for more.

    Dependent on the ``figure3d`` argument, either a 3D figure object is created that inherits from `~.plot.Template3D` and `.codes.planar.plot.PerfectMeasurements.Figure`, or the 2D `.codes.planar.plot.PerfectMeasurements.Figure` is used.

    Parameters
    ----------
    args
        Positional arguments are passed on to `.codes.planar.sim.FaultyMeasurements`.
    figure3d
        Enables plotting on a 3D lattice. Disable to plot layer-by-layer on a 2D lattice, which increases responsiveness.
    kwargs
        Keyword arguments are passed on to `.codes.planar.sim.FaultyMeasurements` and the figure object.
    """

    class Figure2D(PerfectMeasurements.Figure, TemplateFM.Figure2D):
        # Inherited docstring
        pass

    class Figure3D(PerfectMeasurements.Figure, TemplateFM.Figure3D):
        # Inherited docstring
        pass
