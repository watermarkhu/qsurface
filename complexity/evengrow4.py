import math
import matplotlib.pyplot as plt
from scipy import optimize
import numpy as np
from progiter import ProgIter

A = 4/147*(3*98)**(1/2)
B = 169/98
C = 134/147

def count_B(S, count=0):

    SE = 2*S/3-4/3

    if SE >= 2:
        count += int(SE)

        SB = S/3+4/3
        SL = S/3-2/3

        count = count_B(SB, count)
        if not isinstance(SL, complex):
            count = count_B(SL, count)
            count = count_B(SL, count)

    return count


def count_C(S, count=0):

    SE = 2*S/3-4/3

    if SE >= 2:
        count += int(SE)

        SB = S/3+4/3
        SL = S/3 - A*(S-B)**(1/2) - C

        count = count_B(SB, count)
        if not isinstance(SL, complex):
            count = count_B(SL, count)
            count = count_B(SL, count)

    return count

def count(S, counter):
    N = math.log(S)/math.log(3)//1
    return counter(S, N)


Mmax = 1000

M = [4+i**2 for i in range(Mmax)]
cb = [count(m, count_B) for m in ProgIter(M)]
cc = [count(m, count_C) for m in ProgIter(M)]


f0 = plt.figure()
plt.plot(M, cb, color="C0", label='Numeric data B: no bound')
plt.plot(M, cc, color="C2", label='Numeric data C: with bound')
plt.plot(M, [2*x*math.log(x)/math.log(27) -2/3*x + 1 for x in M], 'r:', label="Analytic function $O(N\log_{27}N$)")
plt.legend()
plt.ylabel("operations")
plt.xlabel("N")
plt.title("Complexity of algorithm")
f0.savefig("../figures/complexity_numeric_vs_analytic.pdf", transparent=True, format="pdf", bbox_inches="tight")
plt.show()

f1 = plt.figure()
bcdiff = [b-c for b,c in zip(cb, cc)]
plt.plot(M, bcdiff, color="C1")
plt.ylabel("operations")
plt.xlabel("N")
plt.title("Difference numeric data B-C")
f1.savefig("../figures/complexity_numeric_bound_difference.pdf", transparent=True, format="pdf", bbox_inches="tight")
plt.show()



def func(x, a):
    return 2*x*np.log(x)/math.log(a) -2/3*x + 1


f2 = plt.figure()
fitb = optimize.curve_fit(func,  M,  cb, bounds=(27, 50))
plt.plot(M, [2*x*math.log(x)/math.log(27) -2/3*x + 1 for x in M], 'r:', label="Analytic function $O(N\log_{27}N$)")
plt.plot(M, cb, color="C0", label='Numeric data B: no bound')
plt.plot(M, [func(x, *fitb[0]) for x in M], 'k:', label="Fit $O(N\log_{{{:.2f}}}N$)".format(fitb[0][0]))
plt.legend()
plt.ylabel("operations")
plt.xlabel("N")
plt.title("Fit for complexity: B")
f2.savefig("../figures/complexity_fit_numeric_B.pdf", transparent=True, format="pdf", bbox_inches="tight")
plt.show()



f3 = plt.figure()
fitc = optimize.curve_fit(func,  M,  cc, bounds=(27, 50))
plt.plot(M, [2*x*math.log(x)/math.log(27) -2/3*x + 1 for x in M], 'r:', label="Analytic function $O(N\log_{27}N$)")
plt.plot(M, cc, color="C2", label='Numeric data C: no bound')
plt.plot(M, [func(x, *fitc[0]) for x in M], 'k:', label="Fit $O(N\log_{{{:.2f}}}N$)".format(fitc[0][0]))
plt.legend()
plt.ylabel("operations")
plt.xlabel("N")
plt.title("Fit for complexity: C")
f3.savefig("../figures/complexity_fit_numeric_C.pdf", transparent=True, format="pdf", bbox_inches="tight")
plt.show()
