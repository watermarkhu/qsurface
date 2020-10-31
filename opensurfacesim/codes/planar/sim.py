from opensurfacesim.codes.elements import AncillaQubit
from ..toric.sim import PerfectMeasurements as ToricPM, FaultyMeasurements as ToricFM


class PerfectMeasurements(ToricPM):
    """Simulation planar code for perfect measurements."""

    name = "planar"

    def init_surface(self, z: float = 0, **kwargs):
        """Initializes the planar surface code on layer ``z``.

        Parameters
        ----------
        z : int or float, optional
            Layer of qubits, ``z=0`` for perfect measurements.
        """
        self.ancilla_qubits[z], self.data_qubits[z], self.pseudo_qubits[z] = {}, {}, {}
        parity = self.init_parity_check

        # Add data qubits to surface
        for y in range(self.size[1]):
            for x in range(self.size[0]):
                self.add_data_qubit((x + 0.5, y), z=z)
        for y in range(self.size[1] - 1):
            for x in range(1, self.size[0]):
                self.add_data_qubit((x, y + 0.5), z=z)

        # Add ancilla qubits to surface
        for y in range(self.size[1]):
            parity(self.add_pseudo_qubit((0, y), z=z, state_type="x"))
            parity(self.add_pseudo_qubit((self.size[0], y), z=z, state_type="x"))
        for y in range(self.size[1]):
            for x in range(self.size[0] - 1):
                parity(self.add_ancilla_qubit((x + 1, y), z=z, state_type="x"))

        for x in range(self.size[0]):
            parity(self.add_pseudo_qubit((x + 0.5, -0.5), z=z, state_type="z"))
            parity(self.add_pseudo_qubit((x + 0.5, self.size[1] - 0.5), z=z, state_type="z"))
        for x in range(self.size[0]):
            for y in range(self.size[1] - 1): 
                parity(self.add_ancilla_qubit((x + 0.5, y + 0.5), z=z, state_type="z"))

    def init_parity_check(self, ancilla_qubit: AncillaQubit, **kwargs):
        """Initiates a parity check measurement.

        For every ancilla qubit on ``(x,y)``, four neighboring data qubits are entangled for parity check measurements. They are stored via the wind-directional keys.

        Parameters
        ----------
        ancilla_qubit : `~.codes.elements.AncillaQubit`
            Ancilla qubit to initialize.
        """
        (x, y), z = ancilla_qubit.loc, ancilla_qubit.z
        checks = {
            (0.5,0): ((x + 0.5), y),
            (-.5,0): ((x - 0.5), y),
            (0,0.5): (x, (y + 0.5)),
            (0,-.5): (x, (y - 0.5)),
        }
        for key, loc in checks.items():
            if loc in self.data_qubits[z]:
                self.entangle_pair(self.data_qubits[z][loc], ancilla_qubit, key)

    def init_logical_operator(self, **kwargs):
        """Initiates the logical operators [x,z] of the planar code."""
        operators = {
            "x": [self.data_qubits[self.decode_layer][(0.5, i)].edges["x"] for i in range(self.size[0])],
            "z": [self.data_qubits[self.decode_layer][(i + 0.5, 0)].edges["z"] for i in range(self.size[1])]
        }
        self.logical_operators = operators
    
    def state_icons(self, z=0, **kwargs):
        """Prints the state of the surface of layer ``z`` to the console using icons."""
        surface = ""
        for y in range(self.size[1]-1):
            surface += self.data_qubits[z][(.5, y)].state_icon(**kwargs)
            for x in range(1, self.size[0]):
                surface += self.ancilla_qubits[z][(x, y)].state_icon(**kwargs)
                surface += self.data_qubits[z][(x+.5, y)].state_icon(**kwargs)
            surface += "\n" + self.ancilla_qubits[z][(.5, y+.5)].state_icon(**kwargs)
            for x in range(1, self.size[0]):
                surface += self.data_qubits[z][(x, y+.5)].state_icon(**kwargs)
                surface += self.ancilla_qubits[z][(x+.5, y+.5)].state_icon(**kwargs)
            surface += "\n"
        surface += self.data_qubits[z][(.5, self.size[1]-1)].state_icon(**kwargs)
        for x in range(1, self.size[0]):
            surface += self.ancilla_qubits[z][(x, self.size[1]-1)].state_icon(**kwargs)
            surface += self.data_qubits[z][(x+.5, self.size[1]-1)].state_icon(**kwargs)
        print(surface, "\n")

class FaultyMeasurements(ToricFM, PerfectMeasurements):
    """Simulation planar code for faulty measurements."""
    pass
