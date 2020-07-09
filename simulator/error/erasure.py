import random


def apply_error(qubit, p_erasure, **kwargs):
    if random.random() < p_erasure:
        qubit.erasure = True
        rand = random.random()
        if rand < 0.25:
            qubit.E[0].state = 1 - qubit.E[0].state
        elif rand >= 0.25 and rand < 0.5:
            qubit.E[1].state = 1 - qubit.E[1].state
        elif rand >= 0.5 and rand < 0.75:
            qubit.E[0].state = 1 - qubit.E[0].state
            qubit.E[1].state = 1 - qubit.E[1].state
    else:
        qubit.erasure = False



def apply_error_list(qubitlist, p_erasure, **kwargs):
    if p_erasure == 0:
        return
    for qubit in qubitlist:
        apply_error(qubit, p_erasure, **kwargs)


def plot_error(plot_obj, qubit, **kwargs):
    pass
