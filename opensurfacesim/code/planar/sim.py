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

from ..toric.sim import PerfectMeasurements as ToricPM, FaultyMeasurements as ToricFM
from typing import Union


numtype = Union[int, float]


class PerfectMeasurements(ToricPM):
    def init_graph_layer(self, z: numtype = 0, **kwargs):
        """Initilizes the planar surface code on layer `z`.

        Parameters
        ----------
        z : int or float, optional
            Layer of qubits, `z=0` for perfect measurements.
        """
        self.ancilla_qubits[z], self.data_qubits[z], self.pseudo_qubits[z] = {}, {}, {}

        # Add data qubits to surface
        for y in self.range:
            for x in self.range:
                self.add_data_qubit((x + 0.5, y), z=z)
        for y in range(self.size - 1):
            for x in range(1, self.size):
                self.add_data_qubit((x, y + 0.5), z=z)

        # Add ancilla qubits to surface
        for yx in self.range:
            self.add_pseudo_qubit((0, yx), z=z, ancilla_type="x")
            self.add_pseudo_qubit((self.size, yx), z=z, ancilla_type="x")
        for yx in self.range:
            for xy in range(self.size - 1):
                star = self.add_ancilla_qubit((xy + 1, yx), z=z, ancilla_type="x")
                self.init_parity_check(star)

        # Add ancillary qubits to dual lattice
        if self.dual:
            for yx in self.range:
                self.add_pseudo_qubit((yx + 0.5, -0.5), z=z, ancilla_type="z")
                self.add_pseudo_qubit((yx + 0.5, self.size - 0.5), z=z, ancilla_type="z")
            for yx in self.range:
                for xy in range(self.size - 1):
                    plaq = self.add_ancilla_qubit((yx + 0.5, xy + 0.5), z=z, ancilla_type="z")
                    self.init_parity_check(plaq)

    def init_logical_operator(self, **kwargs) -> None:
        """Inititates the logical operators."""
        operators = {
            "x": [self.data_qubits[self.decode_layer][(i + 0.5, 0)].edges["x"] for i in self.range]
        }
        if self.dual:
            operators.update({
                "z": [self.data_qubits[self.decode_layer][(0.5, i)].edges["z"] for i in self.range]
            })
        self.logical_operators = operators


class FaultyMeasurements(PerfectMeasurements, ToricFM):
    """Simulation planar code for faulty measurements."""
    pass
