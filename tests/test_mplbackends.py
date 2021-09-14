from qsurface.main import *
import matplotlib as mpl
import pytest
from .variables import *


backends = ["TkAgg", "Qt5Agg"]


@pytest.mark.plotting
@pytest.mark.parametrize(
    "faulty, figure3d, size",
    [
        (False, False, SIZE_PM),
        (True, False, SIZE_FM),
        (True, True, SIZE_FM),
    ],
)
@pytest.mark.parametrize("backend", backends)
def test_initialize_plot(size, faulty, figure3d, backend):
    """Test all code figures configurations."""
    mpl.use(backend)
    code, decoder = initialize(
        size,
        CODES[0],
        DECODERS[0],
        enabled_errors=ERRORS,
        faulty_measurements=faulty,
        plotting=True,
        plot_params=no_wait_param,
        figure3d=figure3d,
    )
    code.figure.close()
