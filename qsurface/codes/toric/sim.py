from ..elements import AncillaQubit
from .._template.sim import PerfectMeasurements as TemplatePM, FaultyMeasurements as TemplateFM


class PerfectMeasurements(TemplatePM):
    # Inherited docstring

    name = "toric"

    def init_surface(self, z: float = 0, **kwargs):
        """Initializes the toric surface code on layer ``z``.

        Parameters
        ----------
        z : int or float, optional
            Layer of qubits, ``z=0`` for perfect measurements.
        """
        self.ancilla_qubits[z], self.data_qubits[z] = {}, {}

        # Add data qubits to surface
        for y in range(self.size[1]):
            for x in range(self.size[0]):
                self.add_data_qubit((x + 0.5, y), z=z, **kwargs)
                self.add_data_qubit((x, y + 0.5), z=z, **kwargs)

        # Add ancilla qubits to surface
        for y in range(self.size[1]):
            for x in range(self.size[0]):
                star = self.add_ancilla_qubit((x, y), z=z, state_type="x", **kwargs)
                self.init_parity_check(star)

        for y in range(self.size[1]):
            for x in range(self.size[0]):
                plaq = self.add_ancilla_qubit((x + 0.5, y + 0.5), z=z, state_type="z", **kwargs)
                self.init_parity_check(plaq)

    def init_parity_check(self, ancilla_qubit: AncillaQubit, **kwargs):
        """Initiates a parity check measurement.

        For every ancilla qubit on ``(x,y)``, four neighboring data qubits are entangled for parity check measurements. They are stored via the wind-directional keys.

        Parameters
        ----------
        ancilla_qubit : `~.codes.elements.AncillaQubit`
            Ancilla-qubit to initialize.
        """
        (x, y), z = ancilla_qubit.loc, ancilla_qubit.z
        checks = {
            (0.5, 0): ((x + 0.5) % self.size[0], y),
            (-0.5, 0): ((x - 0.5) % self.size[0], y),
            (0, 0.5): (x, (y + 0.5) % self.size[1]),
            (0, -0.5): (x, (y - 0.5) % self.size[1]),
        }
        for key, loc in checks.items():
            if loc in self.data_qubits[z]:
                self.entangle_pair(self.data_qubits[z][loc], ancilla_qubit, key)

    def init_logical_operator(self, **kwargs):
        """Initiates the logical operators [x1, x2, z1, z2] of the toric code."""
        operators = {
            "x1": [self.data_qubits[self.decode_layer][(i, 0.5)].edges["x"] for i in range(self.size[0])],
            "x2": [self.data_qubits[self.decode_layer][(0.5, i)].edges["x"] for i in range(self.size[1])],
            "z1": [self.data_qubits[self.decode_layer][(i + 0.5, 0)].edges["z"] for i in range(self.size[0])],
            "z2": [self.data_qubits[self.decode_layer][(0, i + 0.5)].edges["z"] for i in range(self.size[1])],
        }
        self.logical_operators = operators

    @staticmethod
    def _parse_boundary_coordinates(size, *args):
        # Inherited docstrings
        options = {-1: [*args]}
        for i, arg in enumerate(args):
            if arg == 0:
                options[i] = [*args]
                options[i][i] = size
        diff = {
            option: sum([abs(args[i] - args[j]) for i in range(len(args)) for j in range(i + 1, len(args))])
            for option, args in options.items()
        }
        return options[min(diff, key=diff.get)]


class FaultyMeasurements(TemplateFM, PerfectMeasurements):
    # Inherited docstring
    pass
