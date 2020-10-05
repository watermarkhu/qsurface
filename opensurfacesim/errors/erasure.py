from typing import List, Optional, Union
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
    plot_properties = {
        "x_error": {"facecolor": "color_x_primary", "edgecolor": "color_qubit_edge"},
        "y_error": {"facecolor": "color_y_primary", "edgecolor": "color_qubit_edge"},
        "z_error": {"facecolor": "color_z_primary", "edgecolor": "color_qubit_edge"},
        "erasure": {"linestyle": "line_style_tertiary"}
    }
    legend_attributes = {
        "X-error": {"mfc": "color_x_primary", "mec": "color_x_primary"},
        "Y-error": {"mfc": "color_y_primary", "mec": "color_y_primary"},
        "Z-error": {"mfc": "color_z_primary", "mec": "color_z_primary"},
        "Erasure": dict(
            mfc="color_background", marker="~$\u25CC$", mec="color_qubit_edge", mew="line_width_secundary", ms=12
        )}

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
            qubit.errors["erasure"] = True
            rand = random.random()
            if rand < 0.25:
                qubit.edges["x"].state = 1 - qubit.edges["x"].state

            elif rand >= 0.25 and rand < 0.5:
                qubit.edges["z"].state = 1 - qubit.edges["z"].state
            elif rand >= 0.5 and rand < 0.75:
                qubit.edges["x"].state = 1 - qubit.edges["x"].state
                qubit.edges["z"].state = 1 - qubit.edges["z"].state


    def get_draw_properties(self, qubit, **kwargs) -> List[str]:

        property_names = []
        if qubit.errors.get("erasure", False):
            property_names.append("erasure")
        if qubit.edges["x"].state and qubit.edges["z"].state:
            property_names.append("y_error")
        elif qubit.edges["x"].state:
            property_names.append("x_error")
        elif qubit.edges["z"].state:
            property_names.append("z_error")
        return property_names