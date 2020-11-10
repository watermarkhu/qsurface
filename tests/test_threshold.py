from opensurfacesim.threshold import *
import opensurfacesim as oss
import pytest
import pandas as pd
import matplotlib.pyplot as plt
from .variables import *


@pytest.fixture
def example_pm_data():
    """Example data returnd by `threshold.run_many`."""
    data = pd.DataFrame.from_dict(
        {
            "p_bitflip": {
                0: 0.09,
                1: 0.095,
                2: 0.1,
                3: 0.105,
                4: 0.11,
                5: 0.09,
                6: 0.095,
                7: 0.1,
                8: 0.105,
                9: 0.11,
                10: 0.09,
                11: 0.095,
                12: 0.1,
                13: 0.105,
                14: 0.11,
            },
            "decoded": {
                0: 1000.0,
                1: 1000.0,
                2: 1000.0,
                3: 1000.0,
                4: 1000.0,
                5: 1000.0,
                6: 1000.0,
                7: 1000.0,
                8: 1000.0,
                9: 1000.0,
                10: 1000.0,
                11: 1000.0,
                12: 1000.0,
                13: 1000.0,
                14: 1000.0,
            },
            "iterations": {
                0: 1000.0,
                1: 1000.0,
                2: 1000.0,
                3: 1000.0,
                4: 1000.0,
                5: 1000.0,
                6: 1000.0,
                7: 1000.0,
                8: 1000.0,
                9: 1000.0,
                10: 1000.0,
                11: 1000.0,
                12: 1000.0,
                13: 1000.0,
                14: 1000.0,
            },
            "no_error": {
                0: 813.0,
                1: 776.0,
                2: 744.0,
                3: 735.0,
                4: 682.0,
                5: 844.0,
                6: 830.0,
                7: 730.0,
                8: 691.0,
                9: 639.0,
                10: 873.0,
                11: 816.0,
                12: 756.0,
                13: 721.0,
                14: 638.0,
            },
            "size": {
                0: 8.0,
                1: 8.0,
                2: 8.0,
                3: 8.0,
                4: 8.0,
                5: 12.0,
                6: 12.0,
                7: 12.0,
                8: 12.0,
                9: 12.0,
                10: 16.0,
                11: 16.0,
                12: 16.0,
                13: 16.0,
                14: 16.0,
            },
        }
    )
    return data


@pytest.mark.parametrize("mp_processes", [1, 2])
def test_run_many(mp_processes):
    """Test threshold runner with varying number of processes."""
    iters = 10
    sizes = [8, 10]
    data = run_many(
        CODES[0],
        DECODERS[0],
        iterations=iters,
        sizes=sizes,
        enabled_errors=["pauli"],
        error_rates=[{"p_bitflip": 0}],
        output="none",
        mp_processes=mp_processes,
    )

    got_sizes = list(data["size"]) == sizes
    got_error = list(data["p_bitflip"]) == [0.0, 0.0]

    assert got_sizes and got_error


@pytest.mark.parametrize("modified_ansatz", [True, False])
def test_fit_data(example_pm_data, modified_ansatz):
    """Load example data and test fitting."""
    fitter = ThresholdFit(modified_ansatz=modified_ansatz)
    fitter.fit_data(example_pm_data, "p_bitflip")


@pytest.mark.plotting
@pytest.mark.parametrize("modified_ansatz", [True, False])
def test_plot_data(example_pm_data, modified_ansatz):
    """Load example data and test plotting."""
    fitter = ThresholdFit(modified_ansatz=modified_ansatz)
    figure = plt.figure()
    fitter.plot_data(example_pm_data, "p_bitflip", figure=figure)
