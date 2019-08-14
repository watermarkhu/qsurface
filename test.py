import run_toric_2D_uf as rt2u
import run_toric_2D_mwpm as rt2m

size = 10
pX = 0.1
pZ = 0.1
pE = 0.0
iters = 4

plot_load = 1
save_file = 0
filename = None
pauli_file = filename + "_pauli" if filename is not None else None
erasure_file = filename + "_erasure" if filename is not None else None
# pauli_file = "P12_maxdistance"
# erasure_file = "E12_no_error"

output = rt2u.single(size, pE, pX, pZ, save_file, erasure_file, pauli_file, plot_load, plot_size=6)
# output = rt2p.multiple(size, iters, pE, pX, pZ, plot_load=plot_load, plot_size=6)


print(output)
