import run_toric_2D_peeling as rt2p

size = 16
pX = 0.11
pZ = 0.0
pE = 0.0
iters = 4

plot_load = 1
save_file = 0
# filename = None
# pauli_file = filename + "_pauli" if filename is not None else None
# erasure_file = filename + "_erasure" if filename is not None else None
pauli_file = "P12_maxdistance"
erasure_file = "E12_no_error"

output = rt2p.single(size, pE, pX, pZ, save_file, erasure_file, pauli_file, plot_load, plot_size=6)
# output = rt2p.multiple(size, iters, pE, pX, pZ, plot_load=plot_load, plot_size=6)


print(output)
