import run_single
import run_multiple
import toric_lat as tl

size = 4
pX = 0.2
pZ = 00
pE = 0.05
iters = 2

load_plot = True

# output = run_single.toric_2D_MWPM(size, pX, pZ, new_errors, write_errors, load_plot)
# output = run_single.toric_2D_peeling(size, pE, pX, pZ, new_errors, write_errors, load_plot)
# output = run_single.planar_2D_MWPM(size, pX, pZ, new_errors, write_errors, load_plot)


# output = run_multiple.toric_2D_MWPM(size, pX, pZ, iters, new_errors, write_errors, load_plot)
# output = run_multiple.toric_2D_peeling(size, pE, pX, pZ, iters, new_errors, write_errors, load_plot)
# output = run_multiple.planar_2D_MWPM(size, pX, pZ, iters, new_errors, write_errors, load_plot)

# print(output)


TL = tl.lattice(size, load_plot)
TL.init_data()
TL.init_plots()
TL.init_erasure(pE)
# TL.init_pauli(pX, pZ)
TL.measure_stab()
TL.get_matching_peeling()
# TL.get_matching_MWPM()
# logical_error = TL.logical_error()
# correct = True if logical_error == [False, False, False, False] else False
# print(correct)
