import run_single
import run_multiple
import toric_lat as tl

size = 10
pX = 0.1
pZ = 0.1
pE = 0.03
iters = 4

plot_load = True
save_file = False
filename = None
pauli_file = filename + "_pauli" if filename is not None else None
erasure_file = filename + "_erasure" if filename is not None else None



# output = run_single.toric_2D_MWPM(size, pX, pZ, save_file, pauli_file, plot_load)
# output = run_single.toric_2D_peeling(size, pE, pX, pZ, save_file, erasure_file, pauli_file, plot_load)
# output = run_single.planar_2D_MWPM(size, pX, pZ, save_file, pauli_file, plot_load)
#
# output = run_multiple.toric_2D_MWPM(size, pX, pZ, iters, plot_load)
# output = run_multiple.toric_2D_peeling(size, pE, pX, pZ, iters, plot_load)
# output = run_multiple.planar_2D_MWPM(size, pX, pZ, iters, plot_load)

# print(output)



TL = tl.lattice(size=size, plot_load=plot_load, pauli_file=pauli_file, erasure_file=erasure_file)
# TL.init_erasure_errors_region(pE=pE, savefile=save_file)
TL.init_pauli_errors(pX=pX, pZ=pZ, savefile=save_file)
TL.measure_stab()
TL.get_matching_peeling()
# TL.get_matching_MWPM()
logical_error = TL.logical_error()
correct = True if logical_error == [False, False, False, False] else False
print(correct)
