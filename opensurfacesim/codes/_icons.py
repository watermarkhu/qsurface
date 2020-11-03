from ..errors._icons import data_qubit_icon, ancilla_qubit_icon
from .toric.sim import PerfectMeasurements as Toric
from .planar.sim import PerfectMeasurements as Planar


def toric_icons(code: Toric, z: float = 0, **kwargs):
    """Prints the state of the surface of layer ``z`` to the console using icons."""
    surface = ""
    for y in range(code.size[1]):
        for x in range(code.size[0]):
            surface += ancilla_qubit_icon(code.ancilla_qubits[z][(x, y)], **kwargs)
            surface += data_qubit_icon(code.data_qubits[z][(x + 0.5, y)], instance=code.instance, **kwargs)
        surface += "\n"
        for x in range(code.size[0]):
            surface += data_qubit_icon(code.data_qubits[z][(x, y + 0.5)], instance=code.instance, **kwargs)
            surface += ancilla_qubit_icon(code.ancilla_qubits[z][(x + 0.5, y + 0.5)], **kwargs)
        surface += "\n"
    print(surface)


def planar_icons(code: Planar, z: float = 0, **kwargs):
    """Prints the state of the surface of layer ``z`` to the console using icons."""
    surface = ""
    for y in range(code.size[1] - 1):
        surface += data_qubit_icon(code.data_qubits[z][(0.5, y)], **kwargs)
        for x in range(1, code.size[0]):
            surface += ancilla_qubit_icon(code.ancilla_qubits[z][(x, y)], **kwargs)
            surface += data_qubit_icon(code.data_qubits[z][(x + 0.5, y)], instance=code.instance, **kwargs)
        surface += "\n" + ancilla_qubit_icon(code.ancilla_qubits[z][(0.5, y + 0.5)], **kwargs)
        for x in range(1, code.size[0]):
            surface += data_qubit_icon(code.data_qubits[z][(x, y + 0.5)], instance=code.instance, **kwargs)
            surface += ancilla_qubit_icon(code.ancilla_qubits[z][(x + 0.5, y + 0.5)], **kwargs)
        surface += "\n"
    surface += data_qubit_icon(code.data_qubits[z][(0.5, code.size[1] - 1)], instance=code.instance, **kwargs)
    for x in range(1, code.size[0]):
        surface += ancilla_qubit_icon(code.ancilla_qubits[z][(x, code.size[1] - 1)], **kwargs)
        surface += data_qubit_icon(code.data_qubits[z][(x + 0.5, code.size[1] - 1)], instance=code.instance, **kwargs)
    print(surface, "\n")
