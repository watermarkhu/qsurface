from opensurfacesim import codes
import opensurfacesim as oss 
import pytest


CODES = codes.CODES
code_types = ["PerfectMeasurements", "FaultyMeasurements"]
no_wait_param = oss.plot.PlotParams(blocking_wait=0.001)


@pytest.mark.parametrize("Code", CODES)
def test_3d_plots(Code):
    """Test for 3d plotting for faulty measurement class codes."""
    code_module = getattr(getattr(getattr(codes, Code), "plot"), "FaultyMeasurements")
    code = code_module(4, figure3d=True, plot_params=no_wait_param)
    code.initialize()
    code.figure.close()

