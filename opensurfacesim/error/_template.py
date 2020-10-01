from abc import ABC, abstractmethod
from ..code._template.elements import DataQubit
from typing import Dict, Tuple, Union


numtype = Union[int, float]


class Error(ABC):
    """Template class for errors.

    Parameters
    ----------
    data_qubits: dict of dict of DataQubit
        Data-qubit database supplied by `code.<type>.init_errors`.

    See Also
    --------
    DataQubit
    """

    def __init__(self, **kwargs) -> None:
        self.default_error_rates = {}
        self.type = str(self.__module__).split(".")[-1]
        self.plot_attributes = {}
        self.legend_attributes = {}

    def __repr__(self) -> str:
        return "{} error object with defaults: {}".format(self.type, self.default_error_rates)

    @abstractmethod
    def apply_error(self, qubit, **kwargs) -> None:
        """Applies the current error type to the `qubit`."""
        pass

    def plot_error(self, qubit) -> None:
        """Optional plotting function associated with the current error type.

        Parameters
        ----------
        qubit : DataQubit

        See Also
        --------
        DataQubit
        """
        pass
