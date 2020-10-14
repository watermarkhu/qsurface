from .._template import PlotCode
from .sim import Toric as SimToric

class Toric(PlotCode, SimToric):

    opposite_keys = dict(n="s", s="n", e="w", w="e")

    def do_decode(self, *args, **kwargs):
        self.uf_figure = self.init_uf_figure() 
        super().do_decode(*args, **kwargs)
        self.code.figure.draw_figure(new_iter_name="Matchings found")
