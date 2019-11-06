import matplotlib.pyplot as plt
from progiter import ProgIter as pg

sizes = 40 ** 2
boundary = [(0, 0)]
cluster = [(0, 0)]
threshold_sizes = [5]


def get_new_v(cluster, boundary, manhattan_dis):
    neighbors = ((-1, 0), (1, 0), (0, -1), (0, 1))

    new_vertices, source_vertices = [], []
    new_neighbors, num_neighbors = set(), 0

    for (y, x) in boundary:
        for dy, dx in neighbors:
            newv = (y + dy, x + dx)
            dis = abs(newv[0]) + abs(newv[1])
            if newv not in cluster:
                if dis == manhattan_dis:
                    source_vertices.append((y, x))
                    new_vertices.append(newv)
                if newv not in new_neighbors:
                    new_neighbors.add(newv)
                    num_neighbors += 1

    if new_vertices != []:

        grow_sizes = []
        for newv in new_vertices:
            newv_extraneighborcount = 0
            for dy, dx in neighbors:
                extra_neighbor = (newv[0] + dy, newv[1] + dx)
                if (
                    extra_neighbor not in boundary
                    and extra_neighbor not in new_neighbors
                ):
                    newv_extraneighborcount += 1

            grow_sizes.append(len(cluster) + num_neighbors + newv_extraneighborcount)

        new_size = min(grow_sizes)
        new_vertex = new_vertices[grow_sizes.index(new_size)]

        remove_bound = []
        sources = [s for v, s in zip(new_vertices, source_vertices) if v == new_vertex]
        for source in sources:
            for dy, dx in neighbors:
                newv = (source[0] + dy, source[1] + dx)
                if newv not in cluster and newv != new_vertex:
                    break
            else:
                remove_bound.append(source)
        return new_vertex, new_size, remove_bound
    else:
        return None


manhattan_dis = 1
for i in pg(range(1, sizes)):

    result = None
    while result is None:
        result = get_new_v(cluster, boundary, manhattan_dis)
        if result is None:
            manhattan_dis += 1
    newv, news, rembound = result
    boundary.append(newv)
    cluster.append(newv)
    threshold_sizes.append(news)
    for remv in rembound:
        boundary.remove(remv)

threshold_sizes
diff = [j - i for i, j in zip(threshold_sizes[:-1], threshold_sizes[1:])]

p = []
k = 0
for i in diff:
    k += 1
    if i == 2:
        p.append(k)
        k = 0
    elif i == 3:
        p.append(0)
        k = 0
print(threshold_sizes[:50])
print(diff[:50])
print(p)
for t in range(20):
    print((t - 1) // 4 + 1 + ((t - 1) % 4 + 2) % 5 // 4)

# sump = [sum(p[:i+1]) for i in range(len(p))]
# print(sump)
# for t in range(len(sump)):
#     print(sump[t], 2*((t-1)//4)**2 + 3*((t-1)//4) + ((t-1)%4 + 1) * ((t-1)//4 + 1) + ((t-1) % 4 + 2)//4)


S = 4
K = int(-7 / 4 + (49 / 16 + (S - 8) / 2) ** (1 / 2)) // 1

PG = 2 * K ** 2 + 3 * K + 1
PG


def mop_growth_HG(size):
    if size == 1:
        return 5
    else:
        K = (-3 / 4 + (9 / 16 + (size - 2) / 2) ** (1 / 2)) // 1
        PG = 6 + 2 * K ** 2 + 7 * K
        id = (size - 2) - 2 * K ** 2 - 3 * K
        if id < K + 1:
            CG = 2
        elif id >= K + 1 and id < 2 * (K + 1):
            CG = 3
        elif id >= 2 * (K + 1) and id < 3 * (K + 1) + 1:
            CG = 4
        else:
            CG = 5
        return int(PG + id + CG)


S = 47
id = S - mop_growth_HG(PG + 1)
id

if id < K + 1:
    CG = id
if id >= K + 1 and id < 2 * (K + 1) + 1:
    CG = id - 1
if id >= 2 * (K + 1) + 1 and id < 3 * (K + 1) + 3:
    CG = id - 2
if id >= 3 * (K + 1) + 3 and id < 4 * (K + 1) + 4:
    CG = id - 3
if id >= 4 * (K + 1) + 4:
    id - 4

CG


for y, x in cluster:
    if (y, x) in boundary:
        plt.plot(x, y, ".", color="r", ms=2)
    else:
        plt.plot(x, y, ".", color="k", ms=2)
ax = plt.gca()
ax.set_aspect("equal")

with open("your_file.txt", "w") as f:
    for item in threshold_sizes:
        f.write("{0:d}\n".format(item))
