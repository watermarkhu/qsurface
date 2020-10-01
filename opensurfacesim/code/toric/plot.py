from typing import List, Tuple, Union
from .sim import PerfectMeasurements as SimPM, FaultyMeasurements as SimFM
from .._template.plot import (
    PerfectMeasurements as TemplatePPM,
    CodePlot2D as TemplateCP2D
)


numtype = Union[str, float]
loctype = Tuple[numtype, numtype]


class PerfectMeasurements(SimPM, TemplatePPM):
    def initialize(self, *args, **kwargs) -> None:
        super().initialize(*args, **kwargs)
        self.figures["code"] = CodePlot2D(self, **kwargs)


class CodePlot2D(TemplateCP2D):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.main_boundary = [-0.25, -0.25, self.code.size + 0.5, self.code.size + 0.5]
        self.legend_loc = (1.3, 0.95)

    def parse_line_locs(self, l1: loctype, l2: loctype) -> Tuple[List[numtype], List[numtype]]:
        def get_min(k1, k2):
            options = {0: [k1, k2]}
            if abs(k1 - k2) > .5:
                if k1 == 0:
                    options[1] = [self.code.size, k2]
                if k2 == 0:
                    options[2] = [k1, self.code.size]
                diff = {option: abs(k1-k2) for option, [k1, k2] in options.items()}
                return options[min(diff, key=diff.get)]
            else:
                return options[0]
        return get_min(l1[0], l2[0]), get_min(l1[1], l2[1])