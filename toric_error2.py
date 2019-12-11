import time
import random
from decimal import Decimal as dec


def init_random_seed(timestamp=None, worker=0, iteration=0):
    if timestamp is None:
        timestamp = time.time()
    seed = "{:.0f}".format(timestamp*10**7) + str(worker) + str(iteration)
    random.seed(dec(seed))
    return seed

def apply_random_seed(seed=None):
    if seed is None:
        seed = init_random_seed()
    if type(seed) is not dec:
        seed = dec(seed)
    random.seed(seed)


def init_erasure(graph, pE=0, toric_plot=None):
    """
    :param pE           probability of an erasure error
    :param savefile     toggle to save the errors to a file

    Initializes an erasure error with probabilty pE, which will take form as a uniformly chosen pauli X and/or Z error.
    """

    if pE != 0:
        for qubit in graph.Q.values():
            if random.random() < pE:
                qubit.erasure = True
                rand = random.random()
                if rand < 0.25:
                    qubit.VXE.state = not qubit.VXE.state
                elif rand >= 0.25 and rand < 0.5:
                    qubit.PZE.state = not qubit.PZE.state
                elif rand >= 0.5 and rand < 0.75:
                    qubit.VXE.state = not qubit.VXE.state
                    qubit.PZE.state = not qubit.PZE.state


def init_pauli(graph, pX=0, pZ=0, toric_plot=None):
    """
    :param pX           probability of a Pauli X error
    :param pZ           probability of a Pauli Z error
    :param savefile     toggle to save the errors to a file

    initates Pauli X and Z errors on the lattice based on the error rates
    """

    if pX != 0 or pZ != 0:
        for qubit in graph.Q.values():
            if pX != 0 and random.random() < pX:
                qubit.VXE.state = not qubit.VXE.state
            if pZ != 0 and random.random() < pZ:
                qubit.PZE.state = not qubit.PZE.state
