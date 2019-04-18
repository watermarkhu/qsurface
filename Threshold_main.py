from toric import toric_lattice
from matplotlib import pyplot as plt
import numpy as np
import time

loadplot = False
new_errors = True
write_errors = False

save_result = True


lattices = [8,12]
p = np.linspace(0.09, 0.11, 2)
Num = 1000

thresholds = np.zeros((len(lattices),len(p)))

for lati in range(len(lattices)):
    for pi in range(len(p)):

        no_error_num = 0
        for i in range(Num):

            if i % 100 == 0:
                print("Iteration", str(i), ": ") #, end="")

            TL = toric_lattice(lattices[lati], loadplot)
            TL.init_errors(p[pi], 0, new_errors, write_errors)
            TL.measure_stab()
            TL.get_matching()
            TL.apply_matching()
            logical_error = TL.logical_error()

            if logical_error == [[False, False],[False, False]]:
                no_error_num += 1


        thresholds[lati, pi] = no_error_num / Num * 100


        print("The threshold for L = ",str(lattices[lati]), "and p =", str(p[pi]), "is", str(thresholds[lati, pi]), "%")
        print("_______________________________________________________________________\n\n")

        time.sleep(0)
    if save_result:
        Name = "./data/Thres_L" + str(lattices[lati]) + "_N" + str(Num) + ".txt"
        np.savetxt(Name, thresholds[lati,:])

fig = plt.figure
for lati in range(len(lattices)):
    plt.plot(p * 100, thresholds[lati, :])

plt.title("performance")
plt.xlabel("p (%)")
plt.ylabel("Decoding success rate (%)")
plt.legend(lattices)
plt.show()
