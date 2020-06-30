
from simulator.graph import graph_2D, graph_3D
from simulator.helper import default_config
from simulator import decoder
import pytest

def test_pymatch():
    testgraph = [[1, 2, 10], [1, 3, 25], [0, 2, 56], [0, 1, 15], [2, 3, 6]]
    result = decoder.blossom.getMatching(4, testgraph)
    assert all([result[result[r]] == r for r in result])


simulator = __import__("simulator")
decoder_names = [decoder for decoder in dir(
    simulator.decoder) if decoder[0] != "_" and decoder != "simulator"]
decoders = [getattr(simulator.decoder, decoder) for decoder in decoder_names]
codes = ["toric", "planar"]
lattice2d, pX2d = [4, 24], [0.01, 0.103]
lattice3d, pX3d = [3, 14], [0.01, 0.04]


@pytest.mark.parametrize("code", codes)
@pytest.mark.parametrize("decoder", decoders)
@pytest.mark.parametrize("size", lattice2d)
@pytest.mark.parametrize("pX", pX2d)
def test2d(code, decoder, size, pX):
    decode = getattr(decoder, code)(**default_config())
    graph = getattr(graph_2D, code)(size, decode, **default_config())
    graph.decoder, decode.graph = decode, graph
    graph.apply_and_measure_errors(pX=pX)
    graph.decoder.decode()
    graph.count_matching_weight()
    logical_error, correct = graph.logical_error()


@pytest.mark.parametrize("code", codes)
@pytest.mark.parametrize("decoder", decoders)
@pytest.mark.parametrize("size", lattice3d)
@pytest.mark.parametrize("pX", pX3d)
def test_toric3d(code, decoder, size, pX):
    decode = getattr(decoder, code)(**default_config())
    graph = getattr(graph_3D, code)(size, decode, **default_config())
    graph.decoder, decode.graph = decode, graph
    graph.apply_and_measure_errors(pX=pX, pmX=pX)
    graph.decoder.decode()
    graph.count_matching_weight()
    logical_error, correct = graph.logical_error()
