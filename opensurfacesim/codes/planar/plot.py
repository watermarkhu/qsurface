from .sim import PerfectMeasurements as SimPM, FaultyMeasurements as SimFM
from .._template.plot import PerfectMeasurements as TemplatePPM, CodePlotPM as TemplateCPPM


class CodePlotPM(TemplateCPPM):
    """Planar code plot for perfect measurements."""

    def __init__(self, code, *args, **kwargs) -> None:
        self.main_boundary = [0, -0.25, code.size, code.size - 0.5]
        self.legend_loc = (1.3, 0.95)
        super().__init__(code, *args, **kwargs)


class PerfectMeasurements(SimPM, TemplatePPM):
    """Plotting planar code class for perfect measurements."""
    FigureClass = CodePlotPM



