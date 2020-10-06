from opensurfacesim.info.benchmark import timeit
from .sim import Code as DecoderTemplate

class Code(DecoderTemplate):
    name = "Template plot decoder",

    @timeit()
    def decode(self, *args, **kwargs):
       self.do_decode(*args, **kwargs)
       self.code.plot_data()
       self.code.plot_ancilla("Decoded.")
