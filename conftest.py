# import pytest
# from simulator.graph import graph_2D, graph_3D


# simulator = __import__("simulator")
# decoder_names = [decoder for decoder in dir(simulator.decoder) if decoder[0] != "_"]
# decoders = [getattr(simulator.decoder, decoder) for decoder in decoder_names]


# @pytest.fixture(params=[(8, "bla")])
# def toric2d(request):
#     print(request.param)
#     return graph_2D.toric(request.param, None)


# @pytest.fixture
# def planar2d(request):
#     return graph_2D.planar(request.param, None)


# @pytest.fixture
# def toric3d(request):
#     return graph_3D.toric(request.param, None)


# @pytest.fixture
# def planar3d(request):
#     return graph_3D.planar(request.param, None)
