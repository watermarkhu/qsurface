from typing import Optional, Union
from ._template import Error as TemplateError
import random


numtype = Union[int, float]


class Error(TemplateError):
    """Pauli error class.

    Parameters
    ----------
    pauli_x : float or int, optional
        Default probability of X-errors or bit-flip errors.
    pauli_z : float or int, optional
        Default probability of Z-errors or phase-flip errors.
    """

    def __init__(self, *args, pauli_x: numtype = 0, pauli_z: numtype = 0, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.default_error_rates = {
            "pauli_x": pauli_x,
            "pauli_z": pauli_z
        }

    def apply_error(self, qubit, pauli_x: Optional[numtype] = None, pauli_z: Optional[numtype] = None, **kwargs):
        """Applies a Pauli error, bit-flip and/or phase-flip.

        Parameters
        ----------
        qubit : DataQubit
            Qubit on which the error is (conditionally) applied.
        pauli_x : float or int, optional
            Overriding probability of X-errors or bit-flip errors.
        pauli_z : float or int, optional
            Overriding probability of Z-errors or phase-flip errors.

        See Also
        --------
        DataQubit
        """
        if pauli_x is None:
            pauli_x = self.default_error_rates["pauli_x"]
        if pauli_z is None:
            pauli_z = self.default_error_rates["pauli_z"]

        if pauli_x != 0 and random.random() < pauli_x:
            qubit.edges["x"].state = not qubit.edges["x"].state
        if pauli_z != 0 and random.random() < pauli_z:
            qubit.edges["z"].state = not qubit.edges["z"].state
