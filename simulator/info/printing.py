'''
2020 Mark Shui Hu

www.github.com/watermarkhu/OpenSurfaceSim
_____________________________________________


Several functions that are used to print the active state of the graph.
'''

import logging
import pyparsing as pp
from pprint import pprint

def printlog(message, print_message=True, log_message=False):
    '''
    Prints the messege to the command window and the log
    '''
    if print_message:
        print(message)
    if log_message:
        logging.warning(message)


def print_configuration(config, iters, **kwargs):
    print("Simulation using settings:")
    settings = {key:value for key, value in kwargs.items() if value != 0}
    settings["iterations"] = iters
    pprint(settings)
    # print("\nusing config:")
    # pprint(config)
    print()


def print_graph(graph, clusters=None, prestring="", poststring=None, printmerged=1, include_even=0, return_string=False):
    """
    :param clusters     either None or a list of clusters
    :param prestring    string to print before evertything else

    This function prints a cluster's size, parity, growth state and appropiate bucket number. If None is inputted, all clusters will be displayed.
    """
    string = ""
    if clusters is None:
        clusters = list(graph.C.values())
        string += "Showing all clusters:\n" if include_even else "Showing active clusters:\n"

    for cluster in clusters:
        if include_even or (not include_even and cluster.bucket is not None):
            if cluster.parent == cluster:
                string += prestring + f"{cluster} (S{cluster.support},"
                string += f"B{cluster.bucket}" if cluster.bucket is not None else "B_"
                string += f",{cluster.on_bound})" if graph.__class__.__name__ == "planar" else ")"

                if cluster.cID != clusters[-1].cID: string += "\n"
            elif printmerged:
                string += str(cluster) + " is merged with " + str(cluster.parent) + ""
                if cluster is not clusters[-1]: string += "\n"
    if poststring is not None:
        string += "\n" + poststring
    if return_string:
        return string
    else:
        printlog(string)


def len_nonAnsi(string):
    '''
    Gets the nonAnsi length of a string, removes additional length of the Ansi formatting of certain strings.
    '''

    ESC = pp.Literal('\x1b')
    integer = pp.Word(pp.nums)
    escapeSeq = pp.Combine(ESC + '[' + pp.Optional(pp.delimitedList(integer,';')) + pp.oneOf(list(pp.alphas)))

    return len(pp.Suppress(escapeSeq).transformString(string))


def print_tree(current_node, childattr='children', nameattr='name', indent='', last='updown'):
    '''
    pptree from https://github.com/clemtoy/pptree
    author: clemtoy

    altered to check length of de-ansi-fied string
    which allows to print colored output (ansi formatting)
    '''

    if hasattr(current_node, nameattr):
        name = lambda node: getattr(node, nameattr)()
    else:
        name = lambda node: str(node)

    children = lambda node: getattr(node, childattr)
    nb_children = lambda node: sum(nb_children(child) for child in children(node)) + 1
    size_branch = {child: nb_children(child) for child in children(current_node)}

    """ Creation of balanced lists for "up" branch and "down" branch. """
    up = sorted(children(current_node), key=lambda node: nb_children(node))
    down = []
    while up and sum(size_branch[node] for node in down) < sum(size_branch[node] for node in up):
        down.append(up.pop())

    """ Printing of "up" branch. """
    for child in up:
        next_last = 'up' if up.index(child) == 0 else ''
        next_indent = '{0}{1}{2}'.format(indent, ' ' if 'up' in last else '│', ' ' * len_nonAnsi(name(current_node)))
        print_tree(child, childattr, nameattr, next_indent, next_last)

    """ Printing of current node. """
    if last == 'up': start_shape = '┌'
    elif last == 'down': start_shape = '└'
    elif last == 'updown': start_shape = ' '
    else: start_shape = '├'

    if up: end_shape = '┤'
    elif down: end_shape = '┐'
    else: end_shape = ''

    print('{0}{1}{2}{3}'.format(indent, start_shape, name(current_node), end_shape))

    """ Printing of "down" branch. """
    for child in down:
        next_last = 'down' if down.index(child) is len(down) - 1 else ''
        next_indent = '{0}{1}{2}'.format(indent, ' ' if 'down' in last else '│', ' ' * len_nonAnsi(name(current_node)))
        print_tree(child, childattr, nameattr, next_indent, next_last)
