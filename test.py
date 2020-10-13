

# opensurfacesim.decoders.mwpm.get_blossom5.run()

# %%
import opensurfacesim
pf = opensurfacesim.codes.toric.plot.PerfectMeasurements(8)
pf.initialize("pauli", "erasure")
dc = opensurfacesim.decoders.mwpm.plot.Toric(pf, check_compatibility=True)

#%%

pf.random_errors(p_erasure=0.07, p_bitflip=0.05, p_phaseflip=0.05)
pf.state_icons()

dc.decode()
pf.state_icons()
print(pf.logical_state, pf.no_error)

# %%
pf.figure.close()



# %%
pf.figure.focus()
# %%
