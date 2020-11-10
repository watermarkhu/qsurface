from opensurfacesim import codes
import pytest
from .variables import *

code_types = ["PerfectMeasurements", "FaultyMeasurements"]


@pytest.mark.plotting
@pytest.mark.parametrize("Code", CODES)
def test_3d_plots(Code):
    """Test for 3d plotting for faulty measurement class codes."""
    code_module = getattr(getattr(getattr(codes, Code), "plot"), "FaultyMeasurements")
    code = code_module(4, figure3d=True, plot_params=no_wait_param)
    code.initialize()
    code.figure.close()
