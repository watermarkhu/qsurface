import numpy as np
import math as m
from math import sqrt
from numpy import kron as kr
from numpy import identity as iden
from matplotlib import pyplot as plt


def vec(string):
    s = np.array(np.mat(string))
    return s


def her(M):
    herM = np.transpose(np.conj(M))
    return herM


def tens(v1, v2):
    mat = np.dot(v1, her(v2))
    return mat


def dens(v1):
    rho = tens(v1, v1)
    return rho


def meas(M, A):
    prob = round(np.trace(np.matmul(M, A)), 4)
    return prob


def cont(A, B, dim):
    C = np.concatenate((A, B), axis=dim)
    return C


def initiate_vects():
    global s0, s1, sp, sm, d00, d01, d10, d11, dpp, dmm, Bphip, Bphim, Bpsip, Bpsim
    s0 = vec("1;0")
    s1 = vec("0;1")
    sp = (s0 + s1) / sqrt(2)
    sm = (s0 - s1) / sqrt(2)
    d00 = kr(s0, s0)
    d01 = kr(s0, s1)
    d10 = kr(s1, s0)
    d11 = kr(s1, s1)
    dpp = kr(sp, sp)
    dmm = kr(sm, sm)
    Bpsip = (d00 + d11) / sqrt(2)
    Bpsim = (d00 - d11) / sqrt(2)
    Bphip = (d01 + d10) / sqrt(2)
    Bphim = (d01 - d10) / sqrt(2)


def initiate_gates():
    global X, Y, Z, H, CX, CY, CZ, XX, YY, ZZ
    X = vec("0 1; 1 0")
    Y = vec("0 -1j; 1j 0")
    Z = vec("1 0; 0 -1")
    H = (X + Z) / sqrt(2)
    CX = kr(dens(s0), iden(2)) + kr(dens(s1), X)
    CY = kr(dens(s0), iden(2)) + kr(dens(s1), Y)
    CZ = kr(dens(s0), iden(2)) + kr(dens(s1), Z)
    XX = kr(X, X)
    YY = kr(Y, Y)
    ZZ = kr(Z, Z)


def cpair(a, b, c, d):
    D = {}
    D[0] = s0
    D[1] = s1
    D[2] = sp
    D[3] = sm
    D["p"] = sp
    D["m"] = sm
    phi = kr(kr(D[a], D[b]), kr(D[c], D[d]))
    return phi


def cpcxz(a, b, c, d):
    phi = cpair(a, b, c, d)
    if a == 1:
        Ax = X
    elif a == 0:
        Ax = iden(2)
    else:
        print("Input must be 0 or 1")

    if b == 1:
        Bx = X
    elif b == 0:
        Bx = iden(2)
    else:
        print("Input must be 0 or 1")

    if c == 1:
        Cz = Z
    elif c == 0:
        Cz = iden(2)
    else:
        print("Input must be 0 or 1")

    if d == 1:
        Dz = Z
    elif d == 0:
        Dz = iden(2)
    else:
        print("Input must be 0 or 1")

    CM = kr(Ax, Bx) @ kr(Cz, Dz)
    Cv = kr(phi, CM)
    return Cv


def gaterho(gate, rho):
    Grho = np.matmul(np.matmul(gate, rho), her(gate))
    return Grho


def measbell(rho):
    ppsip = meas(dens(Bpsip), rho)
    ppsim = meas(dens(Bpsim), rho)
    pphip = meas(dens(Bphip), rho)
    pphim = meas(dens(Bphim), rho)
    pbell = [ppsip, ppsim, pphip, pphim]
    return pbell


def wernerrho(F):
    rho = F * dens(Bpsip) + (1 - F) / 3 * (dens(Bpsim) + dens(Bphip) + dens(Bphim))
    return rho


def reconwerner(rho):
    wbase = measbell(rho)
    nbase = wbase / np.sum(wbase)
    # reconrho = rho/np.sum(rho[:])
    reconrho = (
        nbase[0] * dens(Bpsip)
        + nbase[1] * dens(Bpsim)
        + nbase[2] * dens(Bphip)
        + nbase[3] * dens(Bphim)
    )
    return (reconrho, nbase[0])


initiate_vects()
initiate_gates()

F = 0.6
rhoW = wernerrho(F)

#####################################################
# Parity projection with a shared ancilla
parity_ancilla = False
if parity_ancilla:
    rhoAB = rhoW
    MXZ = (kr(d00, iden(4)) + kr(d01, ZZ) + kr(d10, XX) + kr(d11, XX @ ZZ)) / 2
    rhoABXZ = MXZ @ rhoAB @ MXZ.T

    Mh0 = dens(kr(kr(sp, sp), iden(4)))

    check_ancilla = meas(Mh0, rhoABXZ)
    print(check_ancilla)


#####################################################
# Parity projection with a shared entangled pair
parity_pair = False
if parity_pair:
    PrhoAB = rhoW
    PMXZ = (
        cpcxz(0, 0, 0, 0) + cpcxz(0, 0, 1, 1) + cpcxz(1, 1, 0, 0) + cpcxz(1, 1, 1, 1)
    ) / 2
    PrhoABXZ = PMXZ @ PrhoAB @ PMXZ.T

    PMh0 = dens(kr(kr(dpp, dpp), iden(4)))
    PMh1 = dens(kr(kr(dpp, dmm), iden(4)))
    PMh2 = dens(kr(kr(dmm, dpp), iden(4)))
    PMh3 = dens(kr(kr(dmm, dmm), iden(4)))

    check_pair = round(
        meas(PMh0, PrhoABXZ)
        + meas(PMh1, PrhoABXZ)
        + meas(PMh2, PrhoABXZ)
        + meas(PMh3, PrhoABXZ),
        4,
    )
    print(check_pair)


################################################################
# Single selection
def single_purification(rho0, rho1):

    CCZZ = (
        kr(dens(d00), iden(4))
        + kr(dens(d01), kr(iden(2), Z))
        + kr(dens(d10), kr(Z, iden(2)))
        + kr(dens(d11), ZZ)
    )

    # Joint state of rho0 and rho1
    rho = kr(rho0, rho1)

    # Apply bilateral CNOT gate
    CXrho = gaterho(CCZZ, rho)

    # Get chances of ma = mb
    p0 = kr(iden(4), dpp)
    p1 = kr(iden(4), dmm)
    check0 = meas(dens(p0), CXrho)
    check1 = meas(dens(p1), CXrho)

    # Get post measurement state
    rhoPost = check0 * (her(p0) @ CXrho @ p0) + check1 * (her(p1) @ CXrho @ p1)

    # normalize state, find Fidelity
    (rhoPostn, F) = reconwerner(rhoPost)

    # Perform Hadamard
    rhopure = gaterho(kr(H, H), rhoPostn)

    return (rhopure, F)


def double_purification(rho0, rho1, rho2):
    CCZZ0 = kr(
        kr(dens(d00), iden(4))
        + kr(dens(d01), kr(iden(2), Z))
        + kr(dens(d10), kr(Z, iden(2)))
        + kr(dens(d11), ZZ),
        iden(4),
    )
    CCZZ2 = kr(
        iden(4),
        kr(iden(4), dens(d00))
        + kr(kr(iden(2), Z), dens(d01))
        + kr(kr(Z, iden(2)), dens(d10))
        + kr(ZZ, dens(d11)),
    )
    # Joint state of rho0 and rho1
    rho = kr(kr(rho0, rho1), rho2)

    # Apply bilateral CNOT gate
    CXrho = gaterho(CCZZ0, rho)
    CXCXrho = gaterho(CCZZ2, CXrho)

    # Get chances of ma = mb

    p0 = kr(kr(iden(4), dpp), dpp)
    p1 = kr(kr(iden(4), dpp), dmm)
    p2 = kr(kr(iden(4), dmm), dpp)
    p3 = kr(kr(iden(4), dmm), dmm)
    check0 = meas(dens(p0), CXCXrho)
    check1 = meas(dens(p1), CXCXrho)
    check2 = meas(dens(p2), CXCXrho)
    check3 = meas(dens(p3), CXCXrho)

    # Get post measurement state
    rhoPost = (
        check0 * (her(p0) @ CXCXrho @ p0)
        + check1 * (her(p1) @ CXCXrho @ p1)
        + check2 * (her(p2) @ CXCXrho @ p2)
        + check3 * (her(p3) @ CXCXrho @ p3)
    )

    # normalize state, find Fidelity
    (rhoPostn, F) = reconwerner(rhoPost)

    # Perform Hadamard
    rhopure = gaterho(kr(H, H), rhoPostn)

    return (rhopure, F)


F_input = [0.6, 0.7, 0.8, 0.9, 0.95]
iters = 8
nested_level = 2

f, (ax1, ax2, ax3) = plt.subplots(1, 3, sharey=True)

for F in F_input:
    F_single = [F]
    F_nested = [F]
    F_double = [F]

    rho0single = wernerrho(F)
    rho0double = wernerrho(F)
    rho0nested = wernerrho(F)
    rho1target = wernerrho(F)
    rho2target = wernerrho(F)

    for i in range(iters):
        (rho0single, F) = single_purification(rho0single, rho1target)
        F_single.append(F)

        rho1nested = rho1target
        for j in range(nested_level - 1):
            (rho0nested, F) = single_purification(rho0nested, rho1nested)
            rho1nested = rho0nested
        F_nested.append(F)

        (rho0double, F) = double_purification(rho0double, rho1target, rho2target)
        F_double.append(F)

    ax1.plot(F_single, ".-")
    ax2.plot(F_nested, ".-")
    ax3.plot(F_double, ".-")

ax1.set_title("Single selection")
ax2.set_title("Nested single selection")
ax3.set_title("Double selection")
ax1.set_xlabel("Input Fidelity")
ax2.set_xlabel("Input Fidelity")
ax3.set_xlabel("Input Fidelity")
ax1.set_ylabel("Max Fidelity")
ax3.legend(F_input)
f.subplots_adjust(hspace=0)
plt.show()


########################################################
# Max entanglement comparison

max_entanglement = False
if max_entanglement:
    F_input = np.linspace(0.5, 1, 51)
    F_thres = 1e-2
    max_it = 50
    nest_level = 4

    F_single = []
    F_nested = []
    F_double = []

    for F in F_input:
        print("Simulating for F = " + str(F))

        rho0cont = wernerrho(F)
        rho1target = wernerrho(F)
        rho2target = wernerrho(F)

        # Single
        it = 0
        F_single_pur = [F]
        (rho0single, Fs) = single_purification(rho0cont, rho1target)
        F_single_pur.append(Fs)
        while (abs(F_single_pur[-2] - F_single_pur[-1]) > F_thres) or it < max_it:
            (rho0single, Fs) = single_purification(rho0single, rho1target)
            F_single_pur.append(Fs)
            it += 1
        F_single.append(F_single_pur[-1])

        # Nested

        rho1nested = rho1target
        for level in range(nest_level - 1):
            it = 0
            F_nested_pur = [F]

            (rho0nested, Fn) = single_purification(rho0cont, rho1nested)
            F_nested_pur.append(Fn)
            while (abs(F_nested_pur[-2] - F_nested_pur[-1]) > F_thres) or it < max_it:
                (rho0nested, Fn) = single_purification(rho0nested, rho1nested)
                F_nested_pur.append(Fn)
                it += 1
            rho1nested = rho0nested

        F_nested.append(F_nested_pur[-1])

        # Double
        it = 0
        F_double_pur = [F]
        (rho0double, Fd) = double_purification(rho0cont, rho1target, rho2target)
        F_double_pur.append(Fd)
        while (abs(F_double_pur[-2] - F_double_pur[-1]) > F_thres) or it < max_it:
            (rho0double, Fd) = double_purification(rho0double, rho1target, rho2target)
            F_double_pur.append(Fd)
            it += 1
        F_double.append(F_double_pur[-1])

    plt.figure(4)
    plt.plot(F_input, F_input)
    plt.plot(F_input, F_single)
    plt.plot(F_input, F_nested)
    plt.plot(F_input, F_double)
    plt.legend(
        [
            "no purification",
            "single selection",
            "nested single selection",
            "double selection",
        ]
    )
    plt.xlabel("Input fidelity")
    plt.ylabel("Max output fidelity")
    plt.show()
