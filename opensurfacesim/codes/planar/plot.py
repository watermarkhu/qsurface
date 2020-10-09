from .sim import PerfectMeasurements as SimPM, FaultyMeasurements as SimFM
from .._template.plot import PerfectMeasurements as TemplatePM


class PerfectMeasurements(SimPM, TemplatePM):
    """Plotting planar code class for perfect measurements."""

    class Figure(TemplatePM.Figure):
        """Planar code plot for perfect measurements."""

        def __init__(self, code, *args, **kwargs) -> None:
            self.main_boundary = [0.25, -0.25, code.size[0]-.5, code.size[1] - .5]
            super().__init__(code, *args, **kwargs)




