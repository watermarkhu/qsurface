from abc import ABC, abstractmethod
from ..codes._template.elements import DataQubit
from typing import Dict, List, Tuple, Union


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
    plot_properties = {}
    legend_attributes = {}

    def __init__(self, **kwargs) -> None:
        self.default_error_rates = {}
        self.type = str(self.__module__).split(".")[-1]

    def __repr__(self) -> str:
        return "{} error object with defaults: {}".format(self.type, self.default_error_rates)

    @abstractmethod
    def apply_error(self, qubit, **kwargs) -> None:
        """Applies the current error type to the `qubit`."""
        pass

    def get_draw_properties(self, qubit, **kwargs) -> List[str]:
        """Optional plotting function associated with the current error type.

        Parameters
        ----------
        qubit : DataQubit

        See Also
        --------
        DataQubit
        """
        return []
