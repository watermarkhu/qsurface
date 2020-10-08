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

opensurfacesim.decoders.mwpm.get_blossom5.run()

# %%
import opensurfacesim
pf = opensurfacesim.codes.planar.plot.PerfectMeasurements(8)
pf.initialize("pauli", "erasure")
dc = opensurfacesim.decoders.mwpm.plot.Planar(pf, check_compatibility=True)

#%%

pf.random_errors(p_erasure=0.07, p_bitflip=0.05, p_phaseflip=0.05)
pf.state_icons()

dc.decode(use_blossom5=1)
pf.state_icons()
print(pf.logical_state, pf.no_error)

# %%
pf.figure.close()



# %%

pf = opensurfacesim.codes.planar.sim.PerfectMeasurements(10)
pf.initialize("pauli")
dc = opensurfacesim.decoders.mwpm.sim.Planar(pf)
succes = []
num = 1000
for _ in range(num):

    pf.apply_errors(pauli_x=0.1)
    dc.decode(use_blossom5=1)
    pf.logical_state
    succes.append(pf.no_error)

print(sum(succes)/num)
# %%

class foo:
    @staticmethod
    def oof(txt):
        print(txt)

class bar(foo):

    @staticmethod
    def foo(txt):
        foo.oof(txt)
        print("done")
# %%
