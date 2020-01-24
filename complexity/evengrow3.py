import matplotlib.pyplot as plt
from scipy import optimize

def count(M,k):
    return -4/3*k**3 - 8*k**2 + (M-41/3)*k + (M-7)

def kmin(M):
    return 1/2*(M+7/3)**(1/2) -2

def maxcount(M):
    return count(M, round(kmin(M)))

def count2(M,k):
    return -4/3*k**3 - 4*k**2 + (M-11/3)*k + (M-1)

def kmin2(M):
    return 1/2*(M+1/3)**(1/2) - 1

def maxcount2(M):
    return count2(M, round(kmin2(M)))

def maxcount2a(M):
    return (3*M+1)*(9*M+3)**(1/2)/27

def ecount(k):
    return 2*sum([maxcount2(2*i+3) for i in range(k+1)])



X = [i for i in range(70)]
M = [50 + 100*i for i in range(100)]
K = []
for m in M:
    C = [k for k in [count(m/2+1,x) + ecount(x) for x in X] if k > 0]
    K.append(max(C))
    plt.plot(X[:len(C)],C, label=str(m))
plt.xlabel("k")
plt.ylabel("Operations")
    # plt.legend()

def func(x, a, b, c):
    return a * x ** b + c
fit = optimize.curve_fit(func,  M,  K)


plt.plot(M,K, 'b--', label="Operations")
plt.plot(M, [func(x, *fit[0]) for x in M], color='red', label="fit")
plt.legend()
plt.ylabel("Calculations")
plt.xlabel("Lattice size")


fit[0]
