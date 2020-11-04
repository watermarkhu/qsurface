from .sim import PerfectMeasurements as SimPM, FaultyMeasurements as SimFM
from .._template.plot import PerfectMeasurements as PlotPM, FaultyMeasurements as PlotFM


class PerfectMeasurements(SimPM, PlotPM):
    # Inherited docstring

    class Figure(PlotPM.Figure):
        # Inherited docstring

        def __init__(self, code, *args, **kwargs) -> None:
            self.main_boundary = [-0.25, -0.25, code.size[0] + 0.5, code.size[1] + 0.5]
            super().__init__(code, *args, **kwargs)


class FaultyMeasurements(SimFM, PlotFM):
    """Plotting code class for faulty measurements.

    Inherits from `.codes.toric.sim.FaultyMeasurements` and `.codes.toric.plot.PerfectMeasurements`. See documentation for these classes for more. 

    Dependent on the ``figure3d`` argument, either a 3D figure object is created that inherits from `~.plot.Template3D` and `.codes.toric.plot.PerfectMeasurements.Figure`, or the 2D `.codes.toric.plot.PerfectMeasurements.Figure` is used. 

    Parameters
    ----------
    args
        Positional arguments are passed on to `.codes.toric.sim.FaultyMeasurements`. 
    figure3d
        Enables plotting on a 3D lattice. Disable to plot layer-by-layer on a 2D lattice, which increases responsiveness.
    kwargs
        Keyword arguments are passed on to `.codes.toric.sim.FaultyMeasurements` and the figure object. 
    
    """
    class Figure2D(PerfectMeasurements.Figure, PlotFM.Figure2D):
        # Inherited docstring
        pass

    class Figure3D(PerfectMeasurements.Figure, PlotFM.Figure3D):
        # Inherited docstring
        pass
