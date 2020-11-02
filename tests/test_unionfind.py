from opensurfacesim.main import *
import opensurfacesim as oss
import pytest
import random
from .errors import get_error_combinations, get_error_keys


CODES = oss.codes.CODES
ERRORS = oss.errors.ERRORS
SIZE_PM = 12
SIZE_FM = 4
ITERS = 100
no_wait_param = oss.plot.PlotParams(blocking_wait=0.001)


@pytest.mark.parametrize("Code", CODES)
@pytest.mark.parametrize("errors", get_error_combinations())
@pytest.mark.parametrize(
    "faulty, size, max_rate, extra_keys",
    [
        (False, SIZE_PM, 0.2, []),
        (True, SIZE_FM, 0.05, ["pm_bitflip", "pm_phaseflip"]),
    ],
)
def test_unionfind_sim(size, Code, errors, faulty, max_rate, extra_keys):
    """Test initialize function for all configurations."""
    Decoder_module = getattr(oss.decoders, "unionfind").sim
    if hasattr(Decoder_module, Code.capitalize()):
        decoder_module = getattr(Decoder_module, Code.capitalize())
        Code_module = getattr(oss.codes, Code).sim
        code_module = getattr(Code_module, "FaultyMeasurements") if faulty else getattr(Code_module, "PerfectMeasurements")
        code = code_module(size)
        code.initialize(*errors)
        decoder = decoder_module(code)
        error_keys = get_error_keys(errors) + extra_keys

        trivial = 0
        for _ in range(ITERS):
            error_rates = {key: random.random() * max_rate for key in error_keys}
            code.random_errors(**error_rates)
            decoder.decode()
            trivial += code.trivial_ancillas

        assert trivial == ITERS

    else:
        assert True


@pytest.mark.parametrize("weighted_growth", [False, True])
@pytest.mark.parametrize("weighted_union", [False, True])
@pytest.mark.parametrize("dynamic_forest", [False, True])
def test_unionfind_options(weighted_growth, weighted_union, dynamic_forest):
    """Test options of unionfind decoder."""
    code, decoder = initialize(SIZE_PM, "toric", "unionfind", enabled_errors=["pauli"])
    trivial = 0
    for _ in range(ITERS):
        code.random_errors(p_bitflip=random.random() * 0.2)
        decoder.decode(
            weighted_growth=weighted_growth,
            weighted_union=weighted_union,
            dynamic_forest=dynamic_forest,
        )
        trivial += code.trivial_ancillas

    assert trivial == ITERS


@pytest.mark.plotting
@pytest.mark.parametrize(
    "faulty, size",
    [
        (False, SIZE_PM),
        (True, SIZE_FM),
    ],
)
def test_unionfind_plot(faulty, size):
    code, decoder = initialize(
        size,
        "toric",
        "unionfind",
        enabled_errors=["pauli"],
        plotting=True,
        plot_params=no_wait_param,
        faulty_measurements=faulty,
    )
    run(
        code,
        decoder,
        error_rates={"p_bitflip": 0.1},
        print_steps=True,
        step_bucket=True,
        step_cluster=True,
        step_cycle=True,
        step_peel=True,
    )
