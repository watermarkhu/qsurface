from abc import ABC, abstractmethod
import os 
from typing import Optional
from ..configuration import flatten_dict, init_config
from ..info.benchmark import timeit, BenchMarker
from ..codes._template.sim import PerfectMeasurements, FaultyMeasurements
from matplotlib.lines import Line2D


class SimCode(ABC):
    '''
    Decoder template class with code specific class methods
    '''
    name = "Template simulation decoder",
    compatibility_measurements = dict(
        PerfectMeasurements = True,
        FaultyMeasurements = True,
    )
    compatibility_errors =  dict(
        pauli=True,
        erasure=True,
    )

    def __init__(self, code : PerfectMeasurements, benchmarker : Optional[BenchMarker] = None, check_compatibility: bool = False, **kwargs):
        
        self.code = code
        self.benchmarker = benchmarker
        current_folder = os.path.dirname(os.path.abspath(__file__))
        file = current_folder + "/decoders.ini"
        config = flatten_dict(init_config(file))
        for key, value in config.items():
            setattr(self, key, value)
        for key, value in kwargs.items():
            setattr(self, key, value)
        
        if check_compatibility:
            self.check_compatibility()
    
    def __repr__(self):
        return "{} decoder ({})".format(self.name, self.__class__.__name__)

    def check_compatibility(self):
        compatible, unspecified = True, False
        code = self.code.__class__.__name__.split(".")[-1]
        if code in self.compatibility_measurements:
            if not self.compatibility_measurements[code]:
                print("❌ Code <{}> is not compatible with this decoder".format(code))
                compatible = False
        else:
            print("❔ Code <{}> compatibility unspecified".format(code))
        for name in self.code.errors:
            if name in self.compatibility_errors:
                if not self.compatibility_errors[name]:
                    print("❌ Error module <{}> is not compatible with this decoder".format(name))
                    compatible = False
            else:
                print("❔ Error Module <{}> compatibility unspecified".format(name))

        if compatible and not unspecified:
            print("✅ This decoder is compatible with the code.")

    @staticmethod
    def get_neighbor(ancilla_qubit, key):
        data_qubit = ancilla_qubit.parity_qubits[key]
        edge = data_qubit.edges[ancilla_qubit.state_type]
        neighbor = edge.nodes[not edge.nodes.index(ancilla_qubit)]
        return neighbor, edge


    @timeit()
    def decode(self, *args, **kwargs):
       self.do_decode(*args, **kwargs)

    @abstractmethod
    def do_decode(*args, **kwargs):
        pass


class PlotCode(SimCode):

    name = "Template plot decoder",
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.line_color_normal = {
            "x": dict(color = self.code.figure.rc["color_edge"]),
            "z": dict(color = self.code.figure.rc["color_edge"])
        }
        self.line_color_match = {
            "x": dict(color = self.code.figure.rc["color_x_secondary"]),
            "z": dict(color = self.code.figure.rc["color_z_secondary"])
        }

    @timeit()
    def decode(self, *args, **kwargs):
        #Inherited docstrings
       self.do_decode(*args, **kwargs)
       self.code.plot_data()
       self.code.plot_ancilla("Decoded.")
    
    def plot_matching_edge(self, line: Optional[Line2D] = None):
        """Plots the matching edge. 

        Based on the colors defined in ``self.line_color_match``, if a `matplotlib.lines.Line2D` object is supplied, the color of the edge is changed. A future change back to its original color is immediately saved in ``figure.future_dict``. 
        """
        if line: 
            figure = self.code.figure
            next_iter = figure.history_iter + 2
            state_type = line.object.state_type
            figure.new_properties(line, self.line_color_match[state_type])
            figure.future_dict[next_iter][line] = self.line_color_normal[state_type]
