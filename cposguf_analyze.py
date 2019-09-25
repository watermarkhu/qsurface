import psycopg2 as pgs
from cposguf import read_config
from collections import defaultdict
from matplotlib import pyplot as plt
from matplotlib.lines import Line2D

# L = [12 + 4*i for i in range(9)] + [None]
P = [i/1000 for i in [90 + i for i in range(21)]]
# P = [0.11]
L = [None]
type = None      # ubuck or vcomb or None
limit = None
minl, maxl = 2, 10
plotnum = 25

def principal(cluster, L):

    midy, midx = cluster[0][0], cluster[0][1]
    for vi, (y, x, _) in enumerate(cluster):
        mirrors = [(y, x), (y - L, x), (y, x - L), (y - L, x - L)]
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
    return cluster


def tupleit(t):
    return tuple(map(tupleit, t)) if isinstance(t, (tuple, list)) else t


def max_dim(cluster):
    maxy, maxx =  cluster[0][0], cluster[0][1]
    for (y, x, _) in cluster:
        maxy = y if y > maxy else maxy
        maxx = x if x > maxx else maxx
    avgm = (maxy**2 + maxx**2)**(1/2)
    return (maxx, avgm)


def rotate(cluster, width):
    new_cluster = []
    for (y, x, td) in cluster:
        if x == width and td == 0:
            vertex = (width, y, 1)
        else:
            vertex = (width + td - 1- x, y, 1 - td)
        new_cluster.append(vertex)
    return tuple(sorted(new_cluster))


def mirror(cluster, width):
    new_cluster = []
    for (y, x, td) in cluster:
        if x == width and td == 0:
            vertex = (y, width, 0)
        else:
            vertex = (y, width + td - 1 - x, td)
        new_cluster.append(vertex)
    return tuple(sorted(new_cluster))


def fetch_count(p, L, type, limit, minl, maxl, maxfetch=100000):

    query = "SELECT lattice, p, vcomb_solved, error_data FROM simulations "
    if L is not None:
        if isinstance(L, int):
            query += "WHERE lattice = " + str(L)
        elif isinstance(L, list):
            query += "WHERE lattice IN " + str(L)
        if p is not None or type is not None:
            query += " AND "
    if p is not None:
        if L is None:
            query += "WHERE "
        if isinstance(p, float):
            query += "p = " + str(p)
        elif isinstance(p, list):
            query += "p IN " + str(p)
        if type is not None:
            query += " AND "
    if type is not None:
        if L is None and p is None:
            query += "WHERE "
        if type == "ubuck":
            query += "ubuck_solved = TRUE "
        elif type == "vcomb":
            query += "vcomb_solved = TRUE "
    if limit is not None:
        query += "LIMIT {}".format(limit)

    comp_id, num_process, iters, sql_config = read_config("./cposguf.ini")
    con = pgs.connect(**sql_config)
    con.set_session(autocommit=True)
    cur = con.cursor()
    print("Executing query...")
    cur.execute(query)

    cluster_data, type_count = {}, [0, 0]
    sims = [cur.fetchone()]

    while sims != [None]:

        print("Fetching data... (be patient)")
        sims += cur.fetchmany(maxfetch)

        print("Counting clusters...")
        for lattice, p, type, array in sims:
            # Get clusters from array data
            clusters, vertices, cnum = defaultdict(list), {}, 0
            for y, x, td in zip(array[0], array[1], array[2]):
                v = (int(y), int(x), int(td))

                neighbors = [(v[0]-1, v[1]+1, 1)] if v[2] == 0 else [(v[0], v[1], 0)]
                neighbors += [(v[0]-1, v[1], 1), (v[0], v[1]-1, 0)]

                nomerged = True
                for n in neighbors:
                    if n in vertices:
                        if nomerged:
                            cluster = vertices[n]
                            vertices[v] = cluster
                            clusters[cluster].append(list(v))
                            nomerged = False
                        else:
                            cluster = vertices[v]
                            merging = vertices[n]
                            for mv in clusters[merging]:
                                vertices[tuple(mv)] = cluster
                            clusters[cluster].extend(clusters[merging])
                            clusters.pop(merging)
                            break
                if nomerged:
                    vertices[v] = cnum
                    clusters[cnum].append(list(v))
                    cnum += 1
            # Remove single clusters
            clusters = [cluster for cluster in clusters.values() if len(cluster) >= minl and len(cluster) <= maxl]
            # Return to principal cluster
            for ci, cluster in enumerate(clusters):
                clusters[ci] = principal(cluster, lattice)
            # Find augmentation of cluster in dict
            for cluster in tupleit(clusters):
                augs, cmid = [], []
                for rot_i in range(4):
                    dim = max_dim(cluster)
                    augs.append(cluster)
                    cmid.append(dim[1])
                    if cluster in cluster_data:
                        cluster_data[cluster][type] += 1
                        break
                    mcluster = mirror(cluster, dim[0])
                    mdim = max_dim(mcluster)
                    augs.append(mcluster)
                    cmid.append(mdim[1])
                    if mcluster in cluster_data:
                        cluster_data[mcluster][type] += 1
                        break
                    cluster = rotate(cluster, dim[0])
                else:
                    cluster = augs[cmid.index(min(cmid))]
                    cluster_data[cluster] = [0, 1] if type else [1, 0]
            type_count[type] += 1
        sims = [cur.fetchone()]
    else:
        cur.close()
        con.close()

    return sorted(cluster_data.items(), key=lambda kv: sum(kv[1]), reverse=True), type_count


def plot_clusters(data, type_count, plotnum, extra=5):

    print("Plotting...")

    fig = plt.figure(figsize=(16,20))
    plotcols = -int(-plotnum**(1/2)//1)
    plotrows = -(-plotnum//plotcols)
    grid = plt.GridSpec(plotrows + extra, plotcols, wspace=0.4, hspace=0.3)

    maxy, maxx = 0, 0
    for cluster, count in data[:plotnum]:
        for (y, x, td) in cluster:
            maxy = y if y > maxy else maxy
            maxx = x if x > maxx else maxx

    for plot_i, (cluster, _) in enumerate(data[:plotnum]):
        ax = plt.subplot(grid[plot_i//plotcols, plot_i%plotcols])
        ax = plt.gca()
        ax.invert_yaxis()
        ax.set_aspect('equal')
        ax.axis('off')
        ax.set_title(str(plot_i))
        for y in range(maxy + 1):
            for x in range(maxx + 1):
                a = 0.9 if (y, x, 0) in cluster else 0.1
                ax.plot([x, x + 1], [y, y], alpha=a, color='C{}'.format(plot_i%10), lw=4)
                a = 0.9 if (y, x, 1) in cluster else 0.1
                ax.plot([x, x], [y, y + 1], alpha=a, color='C{}'.format(plot_i%10), lw=4)

    ax_count1 = plt.subplot(grid[plotrows:,:2])
    ax_count2 = plt.subplot(grid[plotrows:,2:])
    ax_count1.set_ylabel("Normalized occurence")
    ax_count2.set_xlabel("Cluster type")

    CU, CV = [], []
    for i, (_, (cu, cv)) in enumerate(data[:plotnum]):
        CU.append(cu/type_count[0])
        CV.append(cv/type_count[0])

    ax_count1.plot(list(range(plotcols)), CU[:plotcols], ':', alpha=0.1, color='black')
    ax_count1.plot(list(range(plotcols)), CV[:plotcols], '--', alpha=0.1, color='black')
    for i in range(plotcols):
        ax_count1.scatter(i, CU[i], s=50, marker='+', color='C{}'.format(i%10))
        ax_count1.scatter(i, CV[i], s=50, marker='x', color='C{}'.format(i%10))
    ax_count2.plot(list(range(plotcols, plotnum)), CU[plotcols:], ':', alpha=0.1, color='black')
    ax_count2.plot(list(range(plotcols, plotnum)), CV[plotcols:], '--', alpha=0.1, color='black')
    for i in range(plotcols, plotnum):
        ax_count2.scatter(i, CU[i], s=50, marker='+', color='C{}'.format(i%10))
        ax_count2.scatter(i, CV[i], s=50, marker='x', color='C{}'.format(i%10))

    legend_elements = [Line2D([0], [0], ls=":", color='black', marker="+", markersize=10, alpha=0.5, label='ubuck'),
                       Line2D([0], [0], ls="--", color='black', marker="x", markersize=10, alpha=0.5, label='vcomb')]

    # Create the figure
    ax_count2.legend(handles=legend_elements)
    plt.title("Cluster data from {} ubuck wins and {} vcomb wins".format(type_count[0], type_count[1]))
    # plt.show()
    return fig


for l, p in [(l, p) for l in L for p in P]:
    print("Now doing L = {}, p {}".format(l,p))

    clusters, count = fetch_count(p, l, type, limit, minl, maxl)
    fig = plot_clusters(clusters, count, plotnum)

    folder = "../../../OneDrive - Delft University of Technology/MEP - thesis Mark/Simulations/cposguf_sim1/"
    file_name = "cposguf_sim1_L-None_p-{0:.3f}".format(p)
    fname = folder + "figures/" + file_name + ".pdf"
    fig.savefig(fname, transparent=True, format="pdf", bbox_inches="tight")
    plt.close(fig)

    f=open(folder + "data/" + file_name + ".txt", 'w')
    for line in clusters:
        f.write(str(line) + "\n")
    f.close()
