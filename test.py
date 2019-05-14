import run_single
import run_multiple

size = 8
pX = 0.1
pZ = 0
pE = 0.05
iters = 2

load_plot = True
new_errors = True
write_errors = True

# output = run_single.toric_2D_MWPM(size, pX, pZ, new_errors, write_errors, load_plot)
# output = run_single.toric_2D_peeling(size, pE, pX, pZ, new_errors, write_errors, load_plot)
# output = run_single.planar_2D_MWPM(size, pX, pZ, new_errors, write_errors, load_plot)


# output = run_multiple.toric_2D_MWPM(size, pX, pZ, iters, new_errors, write_errors, load_plot)
# output = run_multiple.toric_2D_peeling(size, pE, pX, pZ, iters, new_errors, write_errors, load_plot)
output = run_multiple.planar_2D_MWPM(size, pX, pZ, iters, new_errors, write_errors, load_plot)

print(output)
