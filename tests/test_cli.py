from opensurfacesim.__main__ import cli
import pytest
from .variables import *

ITERS = [1, 10]
PROCESSES = [1, 2]


@pytest.mark.parametrize(
    "faulty, size",
    [
        (False, SIZE_PM),
        (True, SIZE_FM),
    ],
)
@pytest.mark.parametrize("processes", PROCESSES)
@pytest.mark.parametrize("iterations", ITERS)
@pytest.mark.parametrize("benchmark", [True, False])
def test_cli_sim(faulty, size, processes, iterations, benchmark):
    args = ["-e", ERRORS[0], "-C", CODES[0], "-D", DECODERS[0]]
    if faulty:
        args.append("-fm")
    args += ["simulation", "-l", str(size), "-n", str(iterations), "-mp", str(processes)]

    if benchmark:
        args += ["benchmark", "-du", "decode", "-cc", "decode", "-vl", "decode"]

    cli(args)


def test_cli_threshold():
    args = ["-e", "pauli", "-D", "mwpm"]
    args += ["threshold", "-l"] + [str(l) for l in [8, 10, 12]]
    args += ["-n", "100"]
    args += ["-o", "none"]
    args += ["--p_bitflip"] + [str(p) for p in [0.09, 0.1, 0.11]]
    args += ["-fc", "p_bitflip"]
    cli(args)
