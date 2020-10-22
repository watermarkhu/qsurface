from .sim import Toric as SimToric, Planar as SimPlanar
from ..unionfind.plot import Toric as PlotToric, Planar as PlotPlanar


class Toric(PlotToric, SimToric):
    def _grow_node_boundary(self, node, *args, **kwargs):
        super()._grow_node_boundary(node, *args, **kwargs)
        if self.config["step_node"]:
            self._draw(f"Node {node._repr_status} grown.")
        

class Planar(Toric, PlotPlanar, SimPlanar):
    pass