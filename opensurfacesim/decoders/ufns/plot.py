from .sim import Toric as SimToric, Planar as SimPlanar
from ..unionfind.plot import Toric as PlotToric, Planar as PlotPlanar


class Toric(PlotToric, SimToric):
    """Union-Find Node-Suspension decoder for the toric lattice with union-find plot. 

    Has all class attributes and methods from `.ufns.sim.Toric`, with additional parameters below. Default values for these parameters can be supplied via a *decoders.ini* file under the section of ``[ufns]``.

    The plotting class initiates a `opensurfacesim.plot` object. For its usage, see :ref:`plot-usage`. 

    Parameters
    ----------
    step_bucket : bool, optional
        Waits for user after every occupied bucket. Default is false.
    step_cluster : bool, optional
        Waits for user after growth of every cluster. Default is false.
    step_node : bool, optional
        Waits for user after growth of every node. Default is false.
    step_cycle : bool, optional
        Waits for user after every edge removed due to cycle detection. Default is false.
    step_peel : bool, optional
        Waits for user after every edge removed during peeling. Default is false.
    """
    def _grow_node_boundary(self, node, *args, **kwargs):
        super()._grow_node_boundary(node, *args, **kwargs)
        if self.config["step_node"]:
            self._draw(f"Node {node._repr_status} grown.")
        

class Planar(Toric, PlotPlanar, SimPlanar):
    """Union-Find Node-Suspension decoder for the planar lattice with union-find plot. 

    Has all class attributes and methods from `.ufns.sim.Planar`, with additional parameters below. Default values for these parameters can be supplied via a *decoders.ini* file under the section of ``[ufns]``.

    The plotting class initiates a `opensurfacesim.plot` object. For its usage, see :ref:`plot-usage`. 

    Parameters
    ----------
    step_bucket : bool, optional
        Waits for user after every occupied bucket. Default is false.
    step_cluster : bool, optional
        Waits for user after growth of every cluster. Default is false.
    step_node : bool, optional
        Waits for user after growth of every node. Default is false.
    step_cycle : bool, optional
        Waits for user after every edge removed due to cycle detection. Default is false.
    step_peel : bool, optional
        Waits for user after every edge removed during peeling. Default is false.
    """
    pass