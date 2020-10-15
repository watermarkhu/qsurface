from ..unionfind import Cluster as UFCluster, Toric as UFToric

class Toric(UFToric):
    """Union-Find Node-Suspension decoder for the toric lattice."""

    name = "Union-Find Node-Suspension"
    short = "ufbb"

    compatibility_measurements = dict(
        PerfectMeasurements=True,
        FaultyMeasurements=False,
    )
    compatibility_errors = dict(
        pauli=True,
        erasure=False,
    )