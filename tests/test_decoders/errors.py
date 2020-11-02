import opensurfacesim as oss
from opensurfacesim.codes.toric.sim import PerfectMeasurements as toric_code
import itertools

ERRORS = oss.errors.ERRORS


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
