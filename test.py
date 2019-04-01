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


size = 8
p = 0.3
TL = Toric_lattice(size, p, False)
TL.init_Z_errors(ploterrors=True, plotstrings = True, new_errors=False, Error_file = "Z_errors.txt")
TL.Z_MWPM(plot=False,plot_iter=250)
TL.showplot()