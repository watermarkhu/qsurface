'''
This file contains functions that are used to augment a cluster
'''
from collections import defaultdict
from matplotlib import pyplot as plt

def flatten(list):
    '''
    flattens a list of lists or tuple of tuples to a 1d list
    '''
    return [item for sublist in list for item in sublist]


def plot_cluster(cluster, maxy=None, maxx=None, ax=None, color='k'):
    '''
    plots a cluster along a lattice with dim [maxy, maxx]
    '''
    if maxy is None or maxx is None:
        if maxy is None:
            maxy, doy = 0, True
        else:
            doy = False
        if maxx is None:
            maxx, dox = 0, True
        else:
            dox = False
        for y, x, _ in cluster:
            maxy = y if doy and y > maxy else maxy
            maxx = x if dox and x > maxx else maxx
    if ax is None:
        plt.figure()
        ax = plt.gca()
    ax.invert_yaxis()
    ax.set_aspect('equal')
    ax.axis('off')

    for y in range(maxy + 1):
        for x in range(maxx + 1):
            a = 0.9 if (y, x, 0) in cluster else 0.1
            ax.plot([x, x + 1], [y, y], alpha=a, color=color, lw=4)
            a = 0.9 if (y, x, 1) in cluster else 0.1
            ax.plot([x, x], [y, y + 1], alpha=a, color=color, lw=4)


def get_neighbor(y, x, td, L):

    # Only check for existing vertices in row after row
    # neighbors = [(y-1, x+1, 1)] if td == 0 else [(y, x, 0)]
    # neighbors += [(y-1, x, 1), (y, x-1, 0)]

    if td:
        return [(y, x, 0), ((y+1)%L, (x-1)%L, 0), ((y-1)%L, x, 1), ((y+1)%L, x, 1), (y, (x-1)%L, 0), ((y+1)%L, x, 0)]
    else:
        return [(y, (x+1)%L, 1), ((y-1)%L, x, 1), (y, (x+1)%L, 0), (y, (x-1)%L, 0), ((y-1)%L, (x+1)%L, 1), (y, x, 1)]


def get_clusters_from_list(list_of_vertices, size):
    '''
    Returns a dict of clusters, with values lists of connected vertices from a list of vertices
    '''
    clusters, vertices, cnum = defaultdict(list), {}, 0
    for y, x, td in list_of_vertices:
        y, x, td = int(y), int(x), int(td)
        v = (y, x, td)

        neighbors = get_neighbor(*v, size)

        nomerged = True
        for n in neighbors:
            if n in vertices:
                if nomerged:
                    cluster = vertices[n]
                    vertices[v], nomerged = cluster, False
                    clusters[cluster].append(v)
                else:
                    cluster, merging = vertices[v], vertices[n]
                    if cluster != merging:
                        for mv in clusters[merging]:
                            vertices[tuple(mv)] = cluster
                        clusters[cluster].extend(clusters[merging])
                        clusters.pop(merging)
                    break
        if nomerged:
            vertices[v] = cnum
            clusters[cnum].append(v)
            cnum += 1
    return clusters


def get_logical_cluster(dict_of_clusters, lattice):
    '''
    returns the clusters which crosses the logical boundary
    '''
    if len(dict_of_clusters) != 1:
        sorted_list = sorted([cluster for cluster in dict_of_clusters.values()], key=lambda k: len(k), reverse=True)
        for cluster in sorted_list:
            ycheck, xcheck = [0]*lattice, [0]*lattice
            for y, x, _ in cluster:
                ycheck[y], xcheck[x] = 1, 1
            if all(ycheck) or all(xcheck):
                break
        return cluster
    elif len(dict_of_clusters) == 1:
        return dict_of_clusters[0]
    else:
        print("No clusters!")
        exit()


def tupleit(t):
    return tuple(map(tupleit, t)) if isinstance(t, (tuple, list)) else t

def listit(t):
    return list(map(listit, t)) if isinstance(t, (tuple, list)) else t


def max_dim(cluster):
    '''
    Gets a cluster's max x coordinate and max diagnal
    '''
    maxy, maxx =  cluster[0][0], cluster[0][1]
    for (y, x, _) in cluster:
        maxy = y if y > maxy else maxy
        maxx = x if x > maxx else maxx
    mdiag = (maxy**2 + maxx**2)**(1/2)
    return (maxx, mdiag)


def principal(cluster, augment=1, ydim=0, xdim=0):
    '''
    returns any cluster to its principal cluster with:
        - only positive coordiates in its vertices
        - minimal weight of its center of mass
    '''
    if augment:
        midy, midx = cluster[0][0], cluster[0][1]
        for vi, (y, x, _) in enumerate(cluster):
            mirrors = [(y + dy, x + dx) for dy in [-ydim, 0, ydim] for dx in [-xdim, 0, xdim]]
            distances = [((midy - y)**2 + (midx - x)**2)**1/2 for (y, x) in mirrors]
            min_yx = mirrors[distances.index(min(distances))]
            cluster[vi][0], cluster[vi][1] = min_yx[0], min_yx[1]
            midy, midx = (vi*midy + min_yx[0])/(vi+1), (vi*midx + min_yx[1])/(vi+1)

    # Get min coordinates
    miny, minx = cluster[0][0], cluster[0][1]
    for (y, x, _) in cluster:
        miny = y if y < miny else miny
        minx = x if x < minx else minx
    # Return to principal by subtraction
    for vi in range(len(cluster)):
        cluster[vi][0] -= miny
        cluster[vi][1] -= minx

    return tupleit(cluster)


def rotate(cluster, xdim):
    '''
    Rotates a cluster counterclockwise
    '''
    new_cluster = []
    for (y, x, td) in cluster:
        qubit = [xdim + td - x, y, 1 - td]
        new_cluster.append(qubit)
    return principal(sorted(new_cluster), augment=0)


def mirror(cluster, xdim):
    '''
    Flips a cluster on its vertical axis
    '''
    new_cluster = []
    for (y, x, td) in cluster:
        qubit = [y, xdim - x + td, td]
        new_cluster.append(qubit)
    return principal(sorted(new_cluster), augment=0)
