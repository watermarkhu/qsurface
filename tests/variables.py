import opensurfacesim as oss
from opensurfacesim.codes.toric.sim import PerfectMeasurements as toric_code
import itertools

CODES = oss.codes.CODES
DECODERS = oss.decoders.DECODERS
ERRORS = oss.errors.ERRORS
no_wait_param = oss.plot.PlotParams(blocking_wait=0.1)
SIZE_PM = 9
SIZE_FM = 3


def get_error_combinations():
    error_combinations = []
    for r in range(1, len(ERRORS) + 1):
        error_combinations += itertools.combinations(ERRORS, r)
    return error_combinations


def get_error_keys(error_names):
    keys = []
    code = toric_code(2)
    for name in error_names:
        error_module = getattr(oss.errors, name).Sim(code)
        keys += list(error_module.default_error_rates.keys())
    return keys
