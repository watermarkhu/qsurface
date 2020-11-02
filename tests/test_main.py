from opensurfacesim.main import *
import opensurfacesim as oss
import pytest


CODES = oss.codes.CODES
DECODERS = oss.decoders.DECODERS
ERRORS = oss.errors.ERRORS
no_wait_param = oss.plot.PlotParams(blocking_wait=0.001)
SIZE_PM = 8
SIZE_FM = 3
SEED = 12345
ITERS = [1, 10]
MP_ITERS = 24


@pytest.mark.parametrize("Code", CODES)
@pytest.mark.parametrize("Decoder", DECODERS)
@pytest.mark.parametrize("error", ERRORS)
@pytest.mark.parametrize(
    "faulty, size",
    [
        (False, SIZE_PM),
        (True, SIZE_FM),
    ],
)
def test_initialize(size, Code, Decoder, error, faulty):
    """Test initialize function for all configurations."""
    initialize(size, Code, Decoder, enabled_errors=[error], faulty_measurements=faulty)


@pytest.mark.parametrize("Code", CODES)
@pytest.mark.parametrize(
    "faulty, figure3d, size",
    [
        (False, False, SIZE_PM),
        (True, False, SIZE_FM),
        (True, True, SIZE_FM),
    ],
)
def test_initialize_plot(size, Code, faulty, figure3d):
    """Test all code figures configurations."""
    code, decoder = initialize(
        size,
        Code,
        DECODERS[0],
        enabled_errors=ERRORS,
        faulty_measurements=faulty,
        plotting=True,
        plot_params=no_wait_param,
        figure3d=figure3d,
    )
    code.figure.close()


@pytest.mark.parametrize("iterations", ITERS)
def test_run(iterations):
    """Test run function for single and multiple iterations."""
    code, decoder = initialize(SIZE_PM, CODES[0], DECODERS[0])
    output = run(code, decoder, iterations=iterations)
    asserted_output = {"no_error": iterations}
    assert output == asserted_output


@pytest.mark.parametrize("iterations", ITERS)
def test_run_benchmark(iterations):
    """Test for run with benchmarking enabled."""
    processed_seed = float(f"{str(SEED)}0")
    code, decoder = initialize(SIZE_PM, CODES[0], DECODERS[0])
    benchmark = BenchmarkDecoder({"decode": ["count_calls", "value_to_list"]})
    output = run(code, decoder, benchmark=benchmark, iterations=iterations, seed=SEED)
    asserted_output = {
        "no_error": iterations,
        "benchmark": {
            "decoded": iterations,
            "iterations": iterations,
            "seed": processed_seed,
            "count_calls/decode/mean": 1.0,
            "count_calls/decode/std": 0.0,
        },
    }
    assert output == asserted_output


def test_run_multiprocess():
    """Test multiprocess function."""
    code, decoder = initialize(SIZE_PM, CODES[0], DECODERS[0])
    output = run_multiprocess(code, decoder, iterations=MP_ITERS, processes=2)
    assert output == {"no_error": MP_ITERS}


def test_run_multiprocess_benchmark():
    """Test multiprocess benchmark that combines multiple benchmarks."""
    code, decoder = initialize(SIZE_PM, CODES[0], DECODERS[0])
    benchmark = BenchmarkDecoder({"decode": ["count_calls", "value_to_list"]})
    output = run_multiprocess(code, decoder, iterations=MP_ITERS, processes=2, benchmark=benchmark, seed=SEED)
    asserted_output = {
        "no_error": MP_ITERS,
        "benchmark": {
            "decoded": MP_ITERS,
            "iterations": MP_ITERS,
            "seed": SEED,
            "count_calls/decode/mean": 1.0,
            "count_calls/decode/std": 0.0,
        },
    }
    assert output == asserted_output
