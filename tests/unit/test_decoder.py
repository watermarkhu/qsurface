
from simulator.configuration import setup_decoder 
from simulator import decoder
import pytest

def test_pymatch():
    testgraph = [[1, 2, 10], [1, 3, 25], [0, 2, 56], [0, 1, 15], [2, 3, 6]]
    result = decoder.modules_blossom5.methods.getMatching(4, testgraph)
    assert all([result[result[r]] == r for r in result])


simulator = __import__("simulator")
decoder_names = [decoder for decoder in dir(
    simulator.decoder) if decoder[0] != "_" and decoder[:7] != "modules" and decoder != "simulator"]
codes = ["toric", "planar"]
lattice2d, pX2d = [4, 24], [0.01]
lattice3d, pX3d = [3, 14], [0.01]


@pytest.mark.parametrize("code", codes)
@pytest.mark.parametrize("decoder_module", decoder_names)
@pytest.mark.parametrize("size", lattice2d)
@pytest.mark.parametrize("pX", pX2d)
def test2d(code, decoder_module, size, pX):
    decoder = setup_decoder(code, decoder_module, size)
    decoder.graph.apply_and_measure_errors(paulix=pX)
    decoder.decode()
    decoder.graph.count_matching_weight()
    logical_error, correct = decoder.graph.logical_error()


@pytest.mark.parametrize("code", codes)
@pytest.mark.parametrize("decoder_module", decoder_names)
@pytest.mark.parametrize("size", lattice3d)
@pytest.mark.parametrize("pX", pX3d)
def test_toric3d(code, decoder_module, size, pX):
    decoder = setup_decoder(code, decoder_module, size, perfect_measurements=False)
    decoder.graph.apply_and_measure_errors(paulix=pX, measurex=pX)
    decoder.decode()
    decoder.graph.count_matching_weight()
    logical_error, correct = decoder.graph.logical_error()
