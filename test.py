

# opensurfacesim.decoders.mwpm.get_blossom5.run()

# %%
import opensurfacesim
pf = opensurfacesim.codes.planar.plot.PerfectMeasurements(4)
pf.initialize("pauli")
dc = opensurfacesim.decoders.unionfind.plot.Planar(pf, check_compatibility=True)

#%%

pf.random_errors(p_bitflip=0.1, p_phaseflip=0.1)
pf.state_icons()

# dc.decode()
dc.decode()
pf.show_corrected()


print(pf.logical_state, pf.no_error)


# # %%
# pf.figure.close()
# %%
pf.figure.focus()

# %%
dc.figure.focus()
# %%
# %%
