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
import opensurfacesim

toric_pm = opensurfacesim.code.toric.sim.PerfectMeasurements(3)
toric_pm.init_errors("pauli")
# %%
import opensurfacesim

toric = opensurfacesim.code.toric.sim.FaultyMeasurements(3)
toric.init_errors("pauli", error_rates=dict(pmx=0.03))
# %%
