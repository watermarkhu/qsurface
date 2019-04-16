from toric import Toric_lattice


def printcode(A):
    size = A.shape
    for row in range(size[0]):
        if (row % 2) == 0:
            line = ""
        else:
            line = "   "
        for col in range(size[1]):
            line += str(A[row, col]) + "     "
        print(line)


size = 6
p = 0.2

loadplot = True
base_image_size = 17
plot_indices = True

plot_lattice = False
plot_errors = False
plot_strings = True
new_errors = True
write_errors = True

TL = Toric_lattice(size, p, loadplot, base_image_size, plot_indices, plot_lattice)
TL.init_Z_errors(plot_errors, plot_strings, new_errors, write_errors)
TL.blossom()
logical_error = TL.logical_error()
print(logical_error)
#TL.Z_MWPM(plot=True,plot_percentage=95, fps = 5)
#TL.showplot()