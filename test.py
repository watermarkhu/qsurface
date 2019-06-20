import run_single
import run_multiple
import toric_lat as tl

size = 6
pX = 0.05
pZ = 0.00
pE = 0.00
iters = 4

load_plot = True
save_file = False
time_stamp = None

# output = run_single.toric_2D_MWPM(size, pX, pZ, save_file, time_stamp, load_plot)
# output = run_single.toric_2D_peeling(size, pE, pX, pZ, save_file, time_stamp, load_plot)
# output = run_single.planar_2D_MWPM(size, pX, pZ, save_file, time_stamp, load_plot)
#
# output = run_multiple.toric_2D_MWPM(size, pX, pZ, iters, save_file, time_stamp, load_plot)
# output = run_multiple.toric_2D_peeling(size, pE, pX, pZ, iters, save_file, time_stamp, load_plot)
# output = run_multiple.planar_2D_MWPM(size, pX, pZ, iters, save_file, time_stamp, load_plot)

# print(output)





TL = tl.lattice(size, load_plot)
TL.init_data()
TL.init_plots()
TL.init_erasure(pE, savefile=save_file, filetimestamp=time_stamp)
TL.init_pauli(pX, pZ, savefile=save_file, filetimestamp=time_stamp)
TL.measure_stab()
TL.get_matching_peeling()
# TL.get_matching_MWPM()
logical_error = TL.logical_error()
correct = True if logical_error == [False, False, False, False] else False
print(correct)
