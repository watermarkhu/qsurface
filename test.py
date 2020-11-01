import opensurfacesim as oss
import pandas as pd

rates = [{"p_bitflip": p} for p in [0.09, 0.095, 0.1, 0.105, 0.11]]
data = oss.threshold.run_many("toric", "mwpm", 1000, [8, 12, 16], ["pauli"], rates)

print(data.to_dict())
