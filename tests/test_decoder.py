from opensurfacesim.main import *
from opensurfacesim.codes.toric.sim import PerfectMeasurements as toric_code
import opensurfacesim as oss
import pytest
import itertools
import random


CODES = oss.codes.CODES
DECODERS = oss.decoders.DECODERS
ERRORS = oss.errors.ERRORS
SIZE_PM = 12
SIZE_FM = 6
ITERS = 100
no_wait_param = oss.plot.PlotParams(blocking_wait=0.001)
error_combinations = []
for r in range(1, len(ERRORS) + 1):
    error_combinations += itertools.combinations(ERRORS, r)


def get_error_keys(error_names):
    keys = []
    code = toric_code(2)
    for name in error_names:
        error_module = getattr(oss.errors, name).Sim(code)
        keys += list(error_module.default_error_rates.keys())
    return keys


@pytest.mark.parametrize("Code", CODES)
@pytest.mark.parametrize("Decoder", DECODERS)
@pytest.mark.parametrize("errors", error_combinations)
@pytest.mark.parametrize(
    "faulty, size, max_rate, extra_keys",
    [
        (False, SIZE_PM, 0.2, []),
        (True, SIZE_FM, 0.05, ["pm_bitflip", "pm_phaseflip"]),
    ],
)
def test_decoder_pm(size, Code, Decoder, errors, faulty, max_rate, extra_keys):
    """Test initialize function for all configurations."""

    Decoder_module = getattr(oss.decoders, Decoder).sim
    if hasattr(Decoder_module, Code.capitalize()):
        decoder_module = getattr(Decoder_module, Code.capitalize())
        Code_module = getattr(oss.codes, Code).sim
        code_module = (
            getattr(Code_module, "FaultyMeasurements")
            if faulty
            else getattr(Code_module, "PerfectMeasurements")
        )
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


def test_get_blossomv():
    oss.decoders.mwpm.get_blossomv()


@pytest.mark.parametrize("weighted_growth", [False, True])
@pytest.mark.parametrize("weighted_union", [False, True])
@pytest.mark.parametrize("dynamic_forest", [False, True])
def test_decoder_unionfind(weighted_growth, weighted_union, dynamic_forest):
    code, decoder = initialize(SIZE_PM, "toric", "unionfind", enabled_errors=["pauli"])
    output = run(
        code,
        decoder,
        error_rates={"p_bitflip": 0.1},
        iterations=ITERS,
        weighted_growth=weighted_growth,
        weighted_union=weighted_union,
        dynamic_forest=dynamic_forest,
    )


@pytest.mark.parametrize(
    "faulty, size",
    [
        (False, SIZE_PM),
        (True, SIZE_FM),
    ],
)
def test_plot_unionfind(faulty, size):
    code, decoder = initialize(
        size,
        "toric",
        "unionfind",
        enabled_errors=["pauli"],
        plotting=True,
        plot_params=no_wait_param,
        faulty_measurements=faulty,
    )
    output = run(
        code,
        decoder,
        error_rates={"p_bitflip": 0.1},
        print_steps=True,
        step_bucket=True,
        step_cluster=True,
        step_cycle=True,
        step_peel=True,
    )


@pytest.mark.parametrize(
    "faulty, size",
    [
        (False, SIZE_PM),
        (True, SIZE_FM),
    ],
)
def test_plot_ufns(faulty, size):
    code, decoder = initialize(
        size,
        "toric",
        "ufns",
        enabled_errors=["pauli"],
        plotting=True,
        plot_params=no_wait_param,
        faulty_measurements=faulty,
    )
    output = run(
        code,
        decoder,
        error_rates={"p_bitflip": 0.1},
        print_steps=True,
        print_tree=True,
        step_bucket=True,
        step_cluster=True,
        step_node=True,
        step_cycle=True,
        step_peel=True,
    )