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


size = 16
p = 0.3


TL = Toric_lattice(size, p, plot=False,base_image_size=17)
TL.init_Z_errors(ploterrors=False, plotstrings = False, new_errors=True)
TL.blossom()
#TL.Z_MWPM(plot=True,plot_percentage=95, fps = 5)
TL.showplot()