from abc import ABC, abstractmethod
from opensurfacesim.configuration import get_attributes, init_config
import os
from ..codes._template.elements import DataQubit
from typing import Dict, List, Tuple, Union
from matplotlib import pyplot as plt


class Sim(ABC):
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

    def __repr__(self) -> str:
        return "{} error object with defaults: {}".format(self.type, self.default_error_rates)

    @abstractmethod
    def random_error(self, qubit, **kwargs) -> None:
        """Applies the current error type to the `qubit`."""
        pass


class Plot(Sim):

    legend_items = []

    def __init__(self, figobj, *args, **kwargs) -> None:
        super().__init__(*args, *kwargs)
        self.figure = figobj

        self.plot_properties = get_attributes(
            figobj, init_config(os.path.dirname(os.path.abspath(__file__)) + "/plot_errors.ini")
        )

        self.legend_properties = get_attributes(
            figobj, init_config(os.path.dirname(os.path.abspath(__file__)) + "/plot_legend.ini")
        )

    def _get_legend_properties(self):
        return {key: self.legend_properties[key] for key in self.legend_items}
