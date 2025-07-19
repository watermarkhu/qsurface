from qsurface.codes.elements import AncillaQubit
from ..toric.sim import PerfectMeasurements as ToricPM, FaultyMeasurements as ToricFM


class PerfectMeasurements(ToricPM):
    # Inherited docstring

    name = "rotated"

    _syndrome_dict = { 0: "x", 1: "z" }

    def init_surface(self, z: float = 0, **kwargs):
        """Initializes the rotated surface code on layer ``z``.

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
                self.add_data_qubit((x, y), z=z, **kwargs)

        # Add ancilla qubits to surface
        if self.size[1] % 2 == 1:
            for y in range(self.size[1] - 1):
                for x in range(self.size[0]):
                    parity(self.add_ancilla_qubit((0.5 - 1 * (y%2) + x, y + 0.5), z=z, state_type=self._syndrome_dict[x%2], **kwargs))
        else:
            commute = -1
            for y in range(self.size[1] - 1):
                for x in range(self.size[0] + commute):
                    commute *= -1
                    parity(self.add_ancilla_qubit((0.5 - 1 * (y%2) + x, y + 0.5), z=z, state_type=self._syndrome_dict[x%2], **kwargs))

        outer_qubits = self.size[0] // 2

        for x in range(outer_qubits): # for first and last row
            parity(self.add_ancilla_qubit((0.5 + 2*x, -0.5), z=z, state_type=self._syndrome_dict[1], **kwargs))
            parity(self.add_ancilla_qubit((self.size[0] - 1.5 - 2*x, self.size[1] - 0.5), z=z, state_type=self._syndrome_dict[1], **kwargs))

        # Add pseudo qubits to surface (boundaries)
        if self.size[1] % 2 == 1:
            for y in range(self.size[1] - 1):
                if y % 2 == 0:
                    parity(self.add_pseudo_qubit((-0.5, y + 0.5), z=z, state_type=self._syndrome_dict[1], **kwargs))
                else:
                    parity(self.add_pseudo_qubit((self.size[0] - 0.5, y + 0.5), z=z, state_type=self._syndrome_dict[1], **kwargs))
        else:
            for y in range(self.size[1] - 1):
                if y % 2 == 0:
                    parity(self.add_pseudo_qubit((-0.5, y + 0.5), z=z, state_type=self._syndrome_dict[1], **kwargs))
                    parity(self.add_pseudo_qubit((self.size[0] - 0.5, y + 0.5), z=z, state_type=self._syndrome_dict[1], **kwargs))

        for x in range(self.size[0]+1):
            if x % 2 == 0 or x >= (outer_qubits)*2:
                parity(self.add_pseudo_qubit((x - 0.5, - 0.5), z=z, state_type=self._syndrome_dict[x % 2], **kwargs))
                parity(self.add_pseudo_qubit((self.size[0] - 0.5 - x, self.size[1] - 0.5), z=z, state_type=self._syndrome_dict[x % 2], **kwargs))

    def init_parity_check(self, ancilla_qubit: AncillaQubit, **kwargs):
        """Initiates a parity check measurement.

        For every ancilla qubit on ``(x,y)``, four neighboring data qubits are entangled for parity check measurements.

        Parameters
        ----------
        ancilla_qubit : `~.codes.elements.AncillaQubit`
            Ancilla qubit to initialize.
        """
        (x, y), z = ancilla_qubit.loc, ancilla_qubit.z
        checks = {
            (0.5, 0.5): ((x + 0.5), (y+0.5)),
            (-0.5, 0.5): ((x - 0.5), (y+0.5)),
            (0.5, -0.5): ((x + 0.5), (y - 0.5)),
            (-0.5, -0.5): ((x - 0.5), (y - 0.5)),
        }
        for key, loc in checks.items():
            if loc in self.data_qubits[z]:
                self.entangle_pair(self.data_qubits[z][loc], ancilla_qubit, key)

    def init_logical_operator(self, **kwargs):
        """Initiates the logical operators [x,z] of the rotated code."""
        operators = {
            "x": [self.data_qubits[self.decode_layer][(i, 0)].edges["x"] for i in range(self.size[0])],
            "z": [self.data_qubits[self.decode_layer][(0, i)].edges["z"] for i in range(self.size[1])],
        }
        self.logical_operators = operators


class FaultyMeasurements(ToricFM, PerfectMeasurements):
    # Inherited docstring

    pass
