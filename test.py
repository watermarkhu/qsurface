#%%

import opensurfacesim

toric_pm = opensurfacesim.code.toric.sim.PerfectMeasurements(3)
toric_fm = opensurfacesim.code.toric.sim.FaultyMeasurements(3)
planar_pm = opensurfacesim.code.planar.sim.PerfectMeasurements(3)
planar_fm = opensurfacesim.code.planar.sim.FaultyMeasurements(3)

print(toric_pm)
print(toric_fm)
print(planar_pm)
print(planar_fm)

# %%
planar_fm.parity_measurement()
planar_fm.get_logical_state()

#%%

from opensurfacesim.code.toric.sim import PerfectMeasurements, FaultyMeasurements
pm = PerfectMeasurements(6)
# %%
class test(object):
    def __init__(self) -> None:
        print(self.__module__)
A = test()
# %%
