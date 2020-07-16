'''
2020 Mark Shui Hu

www.github.com/watermarkhu/OpenSurfaceSim
_____________________________________________

We define the unit cell, which contains two qubits, a star operator and plaquette operator.

    |       |
- Star  -  Q_0 -     also top (T) qubit
    |       |
-  Q_1  - Plaq  -    also down (D) qubit
    |       |

Each cell is indicated by its y and x coordiantes. As such every qubit and stabilizer can by identified by a unique ID number:

Qubits: qID (td, y, x)          Stabilizers: sID (ertype, y, x)
    Q_0:    (0, y, x)               Star:   (0, y, x)
    Q_1:    (1, y, x)               Plaq:   (1, y, x)

The 2D graph (toric/planar) is a square lattice with 1 layer of these unit cells.
'''


from . import toric

class perfect_measurements(toric.perfect_measurements):

    def __init__(self, *args, **kwargs):
        self.BQ = {}
        super().__init__(*args, **kwargs)


    def init_graph_layer(self, z=0):
        '''
        param z     layer
        Initializes a layer of the graph structure of a toric lattice
        '''
        self.AQ[z], self.DQ[z], self.BQ[z] = {}, {}, {}

        for y in self.range:
            for x in self.range:
                self.add_data_qubit(x+.5, y, z)

        for y in range(self.size - 1):
            for x in range(1, self.size):
                self.add_data_qubit(x, y+.5, z)

        for yx in self.range:
            self.add_boundary(0, yx, z, Type="bstar")
            self.add_boundary(self.size, yx, z, Type="bstar")

        for yx in self.range:
            for xy in range(self.size - 1):
                star = self.add_ancilla_qubit(xy+1, yx, z, "X")
                self.setup_parity(star, report_error=False)

        if self.phaseflip:
            for yx in self.range:
                self.add_boundary(yx+.5, -.5, z, Type="bplaq")
                self.add_boundary(yx+.5, self.size-.5, z, Type="bplaq")

            for yx in self.range:
                for xy in range(self.size - 1):
                    plaq = self.add_ancilla_qubit(yx+.5, xy+.5, z, "Z")
                    self.setup_parity(plaq, report_error=False)

    def init_logical_operator(self, **kwargs):
        self.logical_operators["X"] = [self.DQ[self.decode_layer][(i+.5)].edges["X"] for i in self.range]
        if self.phaseflip:
            self.logical_operators["Z"] = [self.DQ[self.decode_layer][(.5, i)].edges["Z"] for i in self.range]

        
    def add_boundary(self, x, y, z, Type="bound", **kwargs):
        boundary = self.elements.Boundary(loc=(x,y,z), Type=Type)
        self.BQ[z][(x,y)] = boundary
        return boundary


class faulty_measurements(toric.faulty_measurements, perfect_measurements):
    pass
