from ..codes.elements import DataQubit, AncillaQubit


def data_qubit_icon(qubit: DataQubit, instance: float = 0, show_erased: bool = False, **kwargs):
    """Returns the qubit state in a colored icon."""
    if show_erased and hasattr(qubit, "erasure") and qubit.erasure == instance:
        return "⚫"
    elif qubit.state["x"] and qubit.state["z"]:
        return "🟡"
    elif qubit.state["x"]:
        return "🔴"
    elif qubit.state["z"]:
        return "🟢"
    else:
        return "⚪"


def ancilla_qubit_icon(qubit: AncillaQubit, measure: bool = False, **kwargs):
    """Returns the qubit state in a colored icon."""
    state = qubit.state if measure else qubit.measured_state
    if qubit.state_type == "x":
        return "🟧" if state else "🟦"
    else:
        return "🔶" if state else "🔷"
