from typing import List, Tuple, Union
from .sim import PerfectMeasurements as SimPM, FaultyMeasurements as SimFM
from .._template.plot import PerfectMeasurements as TemplatePPM, CodePlot2D as TemplateCP2D

numtype = Union[str, float]
loctype = Tuple[numtype, numtype]


class PerfectMeasurements(SimPM, TemplatePPM):
    def initialize(self, *args, **kwargs) -> None:
        super().initialize(*args, **kwargs)
        self.figures["code"] = CodePlot2D(self, **kwargs)


class CodePlot2D(TemplateCP2D):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.main_boundary = [0, -0.25, self.code.size, self.code.size - 0.5]
        self.legend_loc = (1.3, 0.95)

    def parse_line_locs(self, l1: loctype, l2: loctype) -> Tuple[List[numtype], List[numtype]]:
        return [l1[0], l2[0]], [l1[1], l2[1]]