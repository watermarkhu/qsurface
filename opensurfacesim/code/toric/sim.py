"""
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
"""


from .._template.elements import AncillaQubit
from .._template.sim import PerfectMeasurements as TemplatePM, FaultyMeasurements as TemplateFM
from typing import Union


numtype = Union[int, float]


class PerfectMeasurements(TemplatePM):
    """Simulation toric code for perfect measurements."""
    def init_surface(self, z: numtype = 0, **kwargs):
        """Initilizes the toric surface code on layer `z`.

        Parameters
        ----------
        z : int or float, optional
            Layer of qubits, `z=0` for perfect measurements.
        """
        self.ancilla_qubits[z], self.data_qubits[z] = {}, {}

        # Add data qubits to surface
        for y in self.range:
            for x in self.range:
                self.add_data_qubit((x + 0.5, y), z=z)
                self.add_data_qubit((x, y + 0.5), z=z)

        # Add ancilla qubits to surface
        for y in self.range:
            for x in self.range:
                star = self.add_ancilla_qubit((x, y), z=z, ancilla_type="x")
                self.init_parity_check(star)

        # Add ancillary qubits to dual lattice
        if self.dual:
            for y in self.range:
                for x in self.range:
                    plaq = self.add_ancilla_qubit((x + 0.5, y + 0.5), z=z, ancilla_type="z")
                    self.init_parity_check(plaq)

    def init_parity_check(self, ancilla_qubit : AncillaQubit, **kwargs) -> None:
        """Inititates a parity check measurement.

        For every ancilla qubit on `(x,y)`, four neighboring data qubits are entangled for parity check measurements. They are stored via the wind-directional keys. 

        Parameters
        ----------
        ancilla_qubit : AncillaQubit
            Ancilla qubit to initialize.

        See Also
        --------
        AncillaQubit
        """
        (x, y), z = ancilla_qubit.loc, ancilla_qubit.z
        checks = {
            "e": ((x + 0.5) % self.size, y),
            "w": ((x - 0.5) % self.size, y), 
            "n": (x, (y + 0.5) % self.size), 
            "s": (x, (y - 0.5) % self.size)
        }
        for key, loc in checks.items():
            self.entangle_pair(self.data_qubits[z][loc], ancilla_qubit, key)

    def init_logical_operator(self, **kwargs) -> None:
        """Inititates the logical operators."""
        operators = {
            "x1": [self.data_qubits[self.decode_layer][(i + 0.5, 0)].edges["x"] for i in self.range],
            "x2": [self.data_qubits[self.decode_layer][(0, i + 0.5)].edges["x"] for i in self.range],
        }
        if self.dual:
            operators.update({
                "z1": [self.data_qubits[self.decode_layer][(i, 0.5)].edges["z"] for i in self.range],
                "z2": [self.data_qubits[self.decode_layer][(0.5, i)].edges["z"] for i in self.range],
            })
        self.logical_operators = operators


class FaultyMeasurements(PerfectMeasurements, TemplateFM):
    """Simulation toric code for faulty measurements."""
    pass