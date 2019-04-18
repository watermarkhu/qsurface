from toric import toric_lattice

size = 8
pX = 0
pZ = 0.09

loadplot = True
new_errors = True
write_errors = True

TL = toric_lattice(size, loadplot)
TL.init_errors(pX, pZ, new_errors, write_errors)
TL.measure_stab()
TL.get_matching()
TL.apply_matching()

# Make squash mathcings

logical_error = TL.logical_error()
print(logical_error)

#TL.plot_corrected()





