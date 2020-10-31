from .sim import PerfectMeasurements as SimPM, FaultyMeasurements as SimFM
from .._template.plot import PerfectMeasurements as PlotPM, FaultyMeasurements as PlotFM


class PerfectMeasurements(SimPM, PlotPM):
    """Plotting toric code class for perfect measurements."""

    class Figure(PlotPM.Figure):
        """Toric code plot for perfect measurements."""

        def __init__(self, code, *args, **kwargs) -> None:
            self.main_boundary = [-0.25, -0.25, code.size[0] + 0.5, code.size[1] + 0.5]
            super().__init__(code, *args, **kwargs)


class FaultyMeasurements(SimFM, PlotFM):
    class Figure2D(PerfectMeasurements.Figure, PlotFM.Figure2D):
        pass
    class Figure3D(PerfectMeasurements.Figure, PlotFM.Figure3D):
        pass