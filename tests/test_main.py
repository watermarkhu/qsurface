#%%
from opensurfacesim.main import *
import opensurfacesim as oss
import pytest

CODES = oss.codes.CODES
DECODERS = oss.decoders.DECODERS
ERRORS = oss.errors.ERRORS
no_wait_param = oss.plot.PlotParams(blocking_wait=0.001)

@pytest.mark.parametrize("Code", CODES)
@pytest.mark.parametrize("Decoder", DECODERS)
@pytest.mark.parametrize("error", ERRORS)
@pytest.mark.parametrize("faulty", [True, False])
def test_initialize(Code, Decoder, error, faulty):
    initialize(6, Code, Decoder, enabled_errors=[error], faulty_measurements=faulty)

@pytest.mark.parametrize("Code", CODES)
@pytest.mark.parametrize("faulty", [True, False])
def test_initialize_plot(Code, faulty):
    code, decoder = initialize(
        3,
        Code,
        DECODERS[0],
        enabled_errors=ERRORS,
        faulty_measurements=faulty,
        plotting=True,
        plot_params=no_wait_param,
    )
    code.figure.close()

@pytest.mark.parametrize("iterations", [1, 10])
def test_run(iterations):
    code, decoder = initialize(8, CODES[0], DECODERS[0])
    output = run(code, decoder, iterations=iterations)
    asserted_output = {"no_error": iterations}
    assert output == asserted_output

@pytest.mark.parametrize("iterations", [1, 10])
def test_run_benchmark(iterations):
    seed = 12345
    processed_seed = float(f"{str(seed)}0")
    code, decoder = initialize(8, CODES[0], DECODERS[0])
    benchmark = BenchmarkDecoder({"decode": ["count_calls", "value_to_list"]})
    output = run(code, decoder, benchmark=benchmark, iterations=iterations, seed=seed)
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
    code, decoder = initialize(8, CODES[0], DECODERS[0])
    output = run_multiprocess(code, decoder, iterations=24, processes=2)
    assert output == {"no_error": 24}
