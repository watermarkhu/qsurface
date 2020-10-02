from .sim import PerfectMeasurements as SimPM, FaultyMeasurements as SimFM
from .._template.plot import PerfectMeasurements as TemplatePPM, CodePlotPM as TemplateCPPM


class PerfectMeasurements(SimPM, TemplatePPM):
    """Plotting toric code class for perfect measurements."""

    def initialize(self, *args, **kwargs) -> None:
        super().initialize(*args, **kwargs)
        self.figure = CodePlotPM(self, **kwargs)


class CodePlotPM(TemplateCPPM):
    """Toric code plot for perfect measurements."""

    def __init__(self, code, *args, **kwargs) -> None:
        self.main_boundary = [-0.25, -0.25, code.size + 0.5, code.size + 0.5]
        self.legend_loc = (1.3, 0.95)
        super().__init__(code, *args, **kwargs)

    def parse_boundary_coordinates(self, *args):
        options = {-1: [*args]}
        for i, arg in enumerate(args):
            if arg == 0:
                options[i] = [*args]
                options[i][i] = self.code.size
        diff = {
            option: sum([abs(args[i] - args[j]) for i in range(len(args)) for j in range(i + 1, len(args))])
            for option, args in options.items()
        }
        return options[min(diff, key=diff.get)]