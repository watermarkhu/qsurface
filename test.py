from toric import Toric_lattice

size = 20
p = 0.5

loadplot = True
base_image_size = 17
plot_indices = False

plot_lattice = False
plot_errors = False
plot_strings = True
new_errors = True
write_errors = False

TL = Toric_lattice(size, p, loadplot, base_image_size, plot_indices, plot_lattice)
TL.init_Z_errors(plot_errors, plot_strings, new_errors, write_errors)
TL.blossom()
l0,l1,l2 = TL.logical_error()
print(l0,l1,l2)
TL.showplot()


