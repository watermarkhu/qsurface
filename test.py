import run_toric_2D_peeling as rt2p

size = 10
pX = 0.1
pZ = 0.0
pE = 0.0
iters = 4

plot_load = 1
save_file = 0
filename = "2019-07-18_11-00-35"
pauli_file = filename + "_pauli" if filename is not None else None
erasure_file = filename + "_erasure" if filename is not None else None



# output = rt2p.single(size, pE, pX, pZ, save_file, erasure_file, pauli_file, plot_load)
output = rt2p.multiple(size, iters, pE, pX, pZ, plot_load=plot_load)


print(output)

# TL = tl.lattice(size=size, plot_load=plot_load, pauli_file=pauli_file, erasure_file=erasure_file)
# TL.init_erasure_errors_region(pE=pE, savefile=save_file)
# TL.init_pauli_errors(pX=pX, pZ=pZ, savefile=save_file)
# TL.measure_stab()
# TL.get_matching_peeling()
# # TL.get_matching_MWPM()
# logical_error = TL.logical_error()
# print(logical_error)
