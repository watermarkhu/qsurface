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


TL = Toric_lattice(size, p, plot=False,base_image_size=27)
TL.init_Z_errors(ploterrors=True, plotstrings = True, new_errors=False)
TL.Z_MWPM(plot=True,plot_percentage=90, fps = 2)
TL.showplot()