'''
2020 Mark Shui Hu

www.github.com/watermarkhu/OpenSurfaceSim
_____________________________________________

Template file for decoder modules
'''

from simulator.configuration import decoderconfig
from simulator.info.benchmark import timeit


class decoder_template(object):
    '''
    Decoder template class with code specific class methods
    '''

    def __init__(self, 
                graph, 
                name = "Template full decoder name",
                config = {},
                benchmarker = None,
                **kwargs):
        
        self.graph = graph
        self.name = name                            # full name of decoder
        self.config = config                        # dict of decoder configurations
        self.benchmarker = benchmarker              # benchmarker object from info.benchmarker

        decoderconfig(self)                         # configuration saved to decoder.ini
        for key, value in kwargs.items():
            setattr(self, key, value)

    @timeit()
    def decode(self, *args, **kwargs):
       '''
       Decoder class must have a decode method
       Decoding time can be timed using the timeit decorator
       '''
       print("No decoding functions have been added yet")


    def reset(self, *args, **kwargs):
        self.graph.reset()
