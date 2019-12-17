from collections import defaultdict as dd

def coordinates(min, max=None):
    if max is None: max = min

    clusters = dd(list)
    clusters[1] = [
            frozenset({(0, 0, 0)})
        ]
    clusters[2] = [
            frozenset({(0, 0, 0), (0, 0, 1)}),
            frozenset({(0, 0, 1), (1, 0, 1)}),
        ]
    clusters[3] = [
            frozenset({(0, 0, 0), (0, 0, 1), (1, 0, 0)}),
            frozenset({(1, 0, 0), (0, 1, 1), (0, 1, 0)}),
            frozenset({(1, 0, 0), (0, 0, 1), (1, 0, 1)}),
            frozenset({(0, 0, 0), (0, 0, 1), (0, 1, 0)}),
            frozenset({(0, 0, 0), (0, 1, 0), (0, 2, 0)})
        ]
    clusters[4] = [
            frozenset({(0, 0, 0), (0, 1, 0), (0, 2, 0), (0, 3, 0)}),
            frozenset({(0, 0, 0), (0, 1, 0), (0, 2, 0), (0, 3, 1)}),
            frozenset({(0, 0, 0), (0, 1, 0), (0, 2, 0), (0, 2, 1)}),
            frozenset({(0, 0, 1), (1, 0, 0), (1, 1, 0), (1, 2, 1)}),
            frozenset({(0, 0, 0), (0, 0, 1), (0, 1, 0), (0, 2, 1)}),
            frozenset({(1, 0, 0), (0, 1, 1), (1, 1, 0), (1, 2, 1)}),
            frozenset({(0, 0, 0), (0, 0, 1), (0, 1, 0), (0, 1, 1)}),
            frozenset({(0, 0, 0), (0, 1, 0), (0, 1, 1), (1, 1, 1)}),
            frozenset({(0, 0, 0), (0, 0, 1), (0, 1, 0), (1, 0, 0)}),
            frozenset({(0, 0, 0), (0, 0, 1), (0, 1, 0), (1, 0, 1)}),
            frozenset({(0, 0, 0), (0, 1, 0), (0, 2, 1), (1, 2, 0)}),
            frozenset({(0, 0, 0), (0, 0, 1), (1, 0, 0), (1, 1, 1)}),
            frozenset({(0, 0, 0), (0, 1, 0), (1, 0, 0), (0, 1, 1)}),
            frozenset({(0, 0, 0), (0, 1, 1), (1, 1, 0), (1, 2, 1)}),
            frozenset({(0, 1, 1), (1, 0, 0), (1, 1, 0), (1, 1, 1)}),
            frozenset({(0, 0, 0), (0, 0, 1), (0, 1, 1), (1, 0, 0)}),
        ]
    clist = []
    for ci in range(min, max+1):
        clist += clusters[ci]
    return clist

coordinates(1,4)
