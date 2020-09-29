from typing import Optional, Union
from ._template import Error as TemplateError
import random


numtype = Union[int, float]


class Error(TemplateError):
    """Erasure error class.

    Parameters
    ----------
    p_erasure : float or int, optional
        Default probability of erasure errors.
    """

    def __init__(self, *args, p_erasure: numtype = 0, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.default_error_rates = {"p_erasure": p_erasure}

    def apply_error(self, qubit, p_erasure: Optional[numtype] = None, **kwargs):
        """Applies an erasure error.

        Parameters
        ----------
        qubit : DataQubit
            Qubit on which the error is (conditionally) applied.
        p_erasure : float or int, optional
            Overriding probability of erasure errors.

        See Also
        --------
        DataQubit
        """
        if p_erasure is None:
            p_erasure = self.default_error_rates["p_erasure"]

        if p_erasure != 0 and random.random() < p_erasure:
            qubit.erasure = True
            rand = random.random()
            if rand < 0.25:
                qubit.edges["x"].state = 1 - qubit.edges["x"].state
            elif rand >= 0.25 and rand < 0.5:
                qubit.edges["z"].state = 1 - qubit.edges["z"].state
            elif rand >= 0.5 and rand < 0.75:
                qubit.edges["x"].state = 1 - qubit.edges["x"].state
                qubit.edges["z"].state = 1 - qubit.edges["z"].state
