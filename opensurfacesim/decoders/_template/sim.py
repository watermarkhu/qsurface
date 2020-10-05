from abc import ABC, abstractmethod
from typing import Optional
from ...configuration import flatten_dict, init_config
from ...info.benchmark import timeit, BenchMarker
from ...codes._template.sim import PerfectMeasurements, FaultyMeasurements

class Code(ABC):
    '''
    Decoder template class with code specific class methods
    '''
    name = "Template decoder",
    compatibility_measurements = dict(
        PerfectMeasurements = True,
        FaultyMeasurements = True,
    )
    compatibility_errors =  dict(
        pauli=True,
        erasure=True,
    )

    def __init__(self, code : PerfectMeasurements, benchmarker : Optional[BenchMarker] = None, **kwargs):
        
        self.code = code
        self.benchmarker = benchmarker

        config = flatten_dict(init_config("decoder.ini"))
        for key, value in config.items():
            setattr(self, key, value)
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def __repr__(self):
        return "{} decoder ({})".format(self.name, self.__class__.__name__)

    def check_compatibility(self):
        
        compatible = True
        code = self.code.__class__.__name__.split(".")[-1]
        if not self.compatibility_measurements[code]:
            print("❌ Code <{}> is not compatible with this decoder".format(code))
            compatible = False
        for name in self.code.errors:
            if not self.compatibility_errors[name]:
                print("❌ Error module <{}> is not compatible with this decoder".format(name))
                compatible = False
        if compatible:
            print("✅ This decoder is compatible with the code.")

    def get_neighbor(self, ancilla_qubit, key):
        data_qubit = ancilla_qubit.parity_qubits[key]
        edge = data_qubit.edges[ancilla_qubit.state_type]
        neighbor = edge.nodes[not edge.nodes.index(ancilla_qubit)]
        return neighbor, edge




    @abstractmethod
    @timeit()
    def decode(self, *args, **kwargs):
       '''Decodes the code.'''
       pass

