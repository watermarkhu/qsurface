import random


def apply_error(qubit, paulix=0, pauliz=0, **kwargs):
    if paulix != 0 and random.random() < paulix:
        qubit.E[0].state = 1 - qubit.E[0].state
    if pauliz != 0 and random.random() < pauliz:
        qubit.E[1].state = 1 - qubit.E[1].state


def apply_error_list(qubitlist, paulix=0, pauliz=0, **kwargs):
    if paulix == 0 and pauliz == 0:
        return
    for qubit in qubitlist:
        apply_error(qubit, paulix, pauliz, **kwargs)


def plot_error(plot_obj, qubit, **kwargs):
    pass
