from .sim import PerfectMeasurements as SimPM, FaultyMeasurements as SimFM
from .._template.plot import PerfectMeasurements as TemplatePPM, CodePlotPM as TemplateCPPM


class CodePlotPM(TemplateCPPM):
    """Toric code plot for perfect measurements."""

    def __init__(self, code, *args, **kwargs) -> None:
        self.main_boundary = [-0.25, -0.25, code.size[0] + 0.5, code.size[1] + 0.5]
        super().__init__(code, *args, **kwargs)

    def parse_boundary_coordinates(self, size, *args):
        options = {-1: [*args]}
        for i, arg in enumerate(args):
            if arg == 0:
                options[i] = [*args]
                options[i][i] = size
        diff = {
            option: sum([abs(args[i] - args[j]) for i in range(len(args)) for j in range(i + 1, len(args))])
            for option, args in options.items()
        }
        return options[min(diff, key=diff.get)]
    
    def init_plot(self, **kwargs) -> None:
        items = [
            self._legend_circle(
                "Vertex",
                ls="-",
                color=self.color_edge,
                mfc=self.color_qubit_face,
                mec=self.color_qubit_edge,
                marker="s",
                ms=5,
            ),
            self._legend_circle(
                "Plaquette",
                ls="--",
                color=self.color_edge,
                mfc=self.color_qubit_face,
                mec=self.color_qubit_edge,
                marker="D",
                ms=5,
            )
        ]
        super().init_plot(legend_items=items, **kwargs)

class PerfectMeasurements(SimPM, TemplatePPM):
    """Plotting toric code class for perfect measurements."""
    FigureClass = CodePlotPM
