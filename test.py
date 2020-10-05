#%%

# import opensurfacesim

# toric_pm = opensurfacesim.code.toric.sim.PerfectMeasurements(3)
# toric_fm = opensurfacesim.code.toric.sim.FaultyMeasurements(3)
# planar_pm = opensurfacesim.code.planar.sim.PerfectMeasurements(3)
# planar_fm = opensurfacesim.code.planar.sim.FaultyMeasurements(3)

# print(toric_pm)
# print(toric_fm)
# print(planar_pm)
# print(planar_fm)

# toric_pm.initialize("pauli", error_rates=dict(pauli_x=0.1))
# toric_fm.initialize("pauli", error_rates=dict(pauli_x=0.03), pmx=0.03)
# planar_pm.initialize("pauli", error_rates=dict(pauli_x=0.1))
# planar_fm.initialize("pauli", error_rates=dict(pauli_x=0.03), pmx=0.03)


# for _ in range(10):
#     toric_pm.simulate()
#     toric_fm.simulate()
#     planar_pm.simulate()
#     planar_fm.simulate()
# %%

import opensurfacesim

sc = opensurfacesim.code.toric.sim.PerfectMeasurements(4)
sc.initialize("pauli")
sc.simulate(pauli_x=0.1)


# %%
import opensurfacesim

pf = opensurfacesim.codes.toric.sim.PerfectMeasurements(4)
pf.initialize("pauli")

dc = opensurfacesim.decoders.mwpm.sim.Toric(pf)
pf.simulate(pauli_x=0.1)
print(pf.logical_state, pf.no_error)
dc.decode()


print(pf.logical_state, pf.no_error)
# pf.plot_errors("Decoded")
# pf.figure.close()



# %%
