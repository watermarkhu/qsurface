

# opensurfacesim.decoders.mwpm.get_blossom5.run()

# %%
import opensurfacesim
pf = opensurfacesim.codes.toric.plot.PerfectMeasurements(10)
pf.initialize("pauli")
dc = opensurfacesim.decoders.unionfind.plot.Toric(pf, check_compatibility=True)

#%%

pf.random_errors(p_bitflip=0.1)
pf.state_icons()

# dc.decode()
dc.decode()



print(pf.logical_state, pf.no_error)


# # %%
# pf.figure.close()
# %%
pf.figure.focus()

# %%
dc.figure.focus()
# %%
# %%
