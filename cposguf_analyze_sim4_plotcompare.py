from cposguf_run import sql_connection, input_error_array, fetch_query
import graph_objects as go
import toric_code as tc
import toric_error as te
import toric_plot as tp
import unionfind as uf
import unionfind_list as ufl
import unionfind_tree as uft
import uf_plot as up
import logging
import printing as pr
from celluloid import Camera
from matplotlib import pyplot as plt
from matplotlib.lines import Line2D


def grow_clusters(
    graph_t,
    uf_plot_t,
    graph_l,
    uf_plot_l,
    plot_step=0,
    print_steps=0,
    random_traverse=0,
):

    """
    Grows the clusters, and merges them until there are no uneven clusters left.
    Starting from the lowest bucket, clusters are popped from the list and grown with {grow_cluster}. Due to the nature of how clusters are appended to the buckets, a cluster needs to be checked for 1) root level 2) bucket level and 3) parity before it can be grown.

    """

    for bucket_i, (bucket_t, bucket_l) in enumerate(
        zip(graph_t.buckets, graph_l.buckets)
    ):

        if bucket_i > max([graph_t.maxbucket, graph_l.maxbucket]):
            break

        if bucket_t == [] and bucket_l == []:
            continue

        if print_steps and bucket_t != []:
            pr.printlog(
            "\n############################ GROW TREE ############################" + f"\nGrowing bucket {bucket_i} of {graph_t.maxbucket}: {bucket_t}" + f"\nRemaining buckets: {graph_t.buckets[bucket_i + 1 : graph_t.maxbucket + 1]}, {graph_t.wastebasket}\n"
            )
            uf_plot_t.waitforkeypress()

        while bucket_t != []:  # Loop over all clusters in the current bucket\
            cluster = bucket_t.pop()
            root_cluster = uf.find_cluster_root(cluster)
            if root_cluster.bucket == bucket_i:
                if print_steps:
                    pr.print_graph(graph_t, [root_cluster], prestring="B: ")
                uft.grow_full(
                    graph_t,
                    root_cluster,
                    root_cluster,
                    root_cluster.support,
                    uf_plot_t,
                    plot_step,
                    print_steps,
                    0,
                    random_traverse,
                    vcomb=0,
                )
            else:
                if print_steps:
                    if root_cluster.bucket is None:
                        pr.printlog(f"{root_cluster} is even.\n")
                    else:
                        if root_cluster.bucket > graph_t.maxbucket:
                            pr.printlog(f"{root_cluster} is already in the wastebasket\n")
                        else:
                            pr.printlog(f"{root_cluster} is already in another bucket.\n")

        uf_plot_t.ax.set_xlabel("")
        if print_steps:
            pr.print_graph(graph_t, printmerged=0)

        if print_steps and bucket_l != []:
            pr.printlog(
            "\n############################ GROW LIST ############################" + f"\nGrowing bucket {bucket_i} of {graph_l.maxbucket}: {bucket_l}" + f"\nRemaining buckets: {graph_l.buckets[bucket_i + 1 : graph_l.maxbucket + 1]}, {graph_l.wastebasket}\n"
            )
            uf_plot_l.waitforkeypress()

        fusion = []  # Initiate Fusion list
        place = []

        for cluster in bucket_l:  # Loop over all clusters in the current bucket
            cluster = uf.find_cluster_root(cluster)

            if (
                cluster.bucket == bucket_i
            ):  # Check that cluster is not already in a higher bucket
                place.append(cluster)

                cluster.boundary[1], cluster.boundary[0] = (
                    cluster.boundary[0],
                    [],
                )  # Set boudary
                cluster.support = (
                    1 - cluster.support
                )  # Grow cluster support for bucket placement
                for vertex, new_edge, new_vertex in cluster.boundary[
                    1
                ]:  # Grow boundaries by half-edge
                    if new_edge.support != 2:
                        new_edge.support += 1
                        if (
                            new_edge.support == 2
                        ):  # Apped to fusion list of edge fully grown
                            fusion.append((vertex, new_edge, new_vertex))
                        else:  # Half grown edges are added immediately to new boundary
                            cluster.boundary[0].append((vertex, new_edge, new_vertex))
                        uf_plot_l.add_edge(new_edge, vertex)
                if plot_step: uf_plot_l.draw_plot(str(cluster) + " grown.")

        if print_steps: mstr = {}
        for base_vertex, edge, grow_vertex in fusion:
            base_cluster = uf.find_cluster_root(base_vertex.cluster)
            grow_cluster = uf.find_cluster_root(grow_vertex.cluster)
            if (
                grow_cluster is None
            ):  # Fully grown edge. New vertex is on the old boundary. Find new boundary on vertex
                base_cluster.add_vertex(grow_vertex)
                uf.cluster_new_vertex(
                    graph_l, base_cluster, grow_vertex, random_traverse=random_traverse
                )
            elif (
                grow_cluster is base_cluster
            ):  # Edge grown on itself. This cluster is already connected. Cut half-edge
                edge.support -= 1
                uf_plot_l.add_edge(edge, base_vertex)
            else:  # Clusters merge by weighted union
                if grow_cluster.size < base_cluster.size:  # apply weighted union
                    base_cluster, grow_cluster = grow_cluster, base_cluster
                if print_steps:  # Keep track of which clusters are merged into one
                    if base_cluster.cID not in mstr:
                        mstr[base_cluster.cID] = pr.print_graph(graph_l, [base_cluster], return_string=True)
                    if grow_cluster.cID not in mstr:
                        mstr[grow_cluster.cID] = pr.print_graph(graph_l, [grow_cluster], return_string=True)
                    mstr[grow_cluster.cID] += "\n" + mstr[base_cluster.cID]
                    mstr.pop(base_cluster.cID)
                uf.union_clusters(grow_cluster, base_cluster)
                grow_cluster.boundary[0].extend(base_cluster.boundary[0])
        if print_steps:
            pr.printlog("")
            for cID, string in mstr.items():
                pr.printlog(f"B:\n{string}\nA:\n{pr.print_graph(graph_l, [graph_l.C[cID]], return_string=True)}\n")

        uf_plot_l.draw_plot("Clusters merged") if plot_step else None

        # Put clusters in new buckets. Some will be added double, but will be skipped by the new_boundary check
        for cluster in place:
            cluster = uf.find_cluster_root(cluster)
            uf.cluster_place_bucket(graph_l, cluster, vcomb=0)

        if print_steps:
            pr.print_graph(graph_l, printmerged=0)

        uf_plot_l.ax.set_xlabel("")

        if not plot_step:
            txt = (
                ""
                if print_steps
                else "Growing bucket #"
                + str(bucket_i)
                + "/"
                + str(max([graph_t.maxbucket, graph_l.maxbucket]))
                + "."
            )
            uf_plot_t.draw_plot(txt)
            uf_plot_l.draw_plot()

    pr.printlog("Clusters grown.")
    uf_plot_t.waitforkeypress()


def plot_final(tp, graph_t, graph_l):
    """
    param: flips        qubits that have flipped in value (y,x)
    param: arrays       data array of the (corrected) qubit states
    plots the applied stabilizer measurements over the lattices
    also, in the qubits that have flipped in value a smaller white circle is plotted

    optionally, the axis is clear and the final state of the lattice is plotted
    """

    plt.sca(tp.ax)

    uc, vc, wc = [0.2, 0, 0.8], [0.2, 0.8, 0], [0.2, 0.8, 0.8]

    for y in range(tp.size):
        for x in range(tp.size):
            for td in range(2):
                u_error = graph_t.E[(0, y, x, td)].matching
                v_error = graph_l.E[(0, y, x, td)].matching

                qubit = tp.qubits[(y, x, td)]

                if u_error and not v_error:
                    qubit.set_edgecolor(uc)
                    tp.ax.draw_artist(qubit)
                elif v_error and not u_error:
                    qubit.set_edgecolor(vc)
                    tp.ax.draw_artist(qubit)
                elif u_error and v_error:
                    qubit.set_edgecolor(wc)
                    tp.ax.draw_artist(qubit)

    uerr = Line2D(
        [0], [0], lw=0, marker="o", color=uc, mfc="w", mew=2, ms=10, label="Tree"
    )
    verr = Line2D(
        [0], [0], lw=0, marker="o", color=vc, mfc="w", mew=2, ms=10, label="List"
    )
    werr = Line2D(
        [0], [0], lw=0, marker="o", color=wc, mfc="w", mew=2, ms=10, label="Both"
    )

    legend1 = plt.legend(
        handles=[uerr, verr, werr],
        bbox_to_anchor=(1.25, 0.95),
        loc="upper right",
        ncol=1,
    )
    tp.ax.add_artist(legend1)

    tp.canvas.blit(tp.ax.bbox)
    pr.printlog("Corrections plotted.")
    tp.waitforkeypress("Corrections plotted")


def plot_both(graph_t, graph_l, seed, p, saveanim=None):

    toric_plot = tp.lattice_plot(graph_t, plot_size=6, line_width=1.5)
    camera = Camera(toric_plot.f) if saveanim is not None else None

    te.apply_random_seed(seed)
    te.init_pauli(graph_t, pX=float(p))
    te.apply_random_seed(seed)
    te.init_pauli(graph_l, pX=float(p))
    toric_plot.plot_errors()

    tc.measure_stab(graph_t, toric_plot)
    tc.measure_stab(graph_l)

    uf_plot_t = up.toric(
        graph_t, toric_plot.f, axn=2, plot_size=10, line_width=1.5, plotstep_click=1, camera=camera
    )
    uf_plot_t.ax.legend().set_visible(False)
    uf_plot_l = up.toric(
        graph_l, toric_plot.f, axn=3, plot_size=10, line_width=1.5, plotstep_click=1, camera=camera
    )

    axes = toric_plot.f.get_axes()
    axes[0].set_title("Peeling lattice")
    axes[1].set_title("tree peeling lattice")
    axes[2].set_title("list peeling lattice")
    if saveanim is not None: camera.snap()

    uf.find_clusters(graph_t, uf_plot=uf_plot_t, plot_step=0, vcomb=0)
    uf.find_clusters(graph_l, uf_plot=uf_plot_l, plot_step=0, vcomb=1)

    grow_clusters(
        graph_t,
        uf_plot_t,
        graph_l,
        uf_plot_l,
        plot_step=0,
        print_steps=1
    )

    uf.peel_clusters(graph_t, uf_plot=uf_plot_t, plot_step=0)
    uf.peel_clusters(graph_l, uf_plot=uf_plot_l, plot_step=0)

    plot_final(toric_plot, graph_t, graph_l)
    if saveanim is not None:
        camera.snap()
        animation = camera.animate(interval=50)
        animation.save(f"./anim/{saveanim}.mp4")

    # Measure logical operator
    graph_t.reset()
    graph_l.reset()


if __name__ == "__main__":

    L = 8
    p = 0.1
    limit = 10
    ftree_tlist = True

    con, cur = sql_connection()
    query = fetch_query(
        "comp_id, created_on, seed", L, p,
        extra="ftree_tlist = " + str(ftree_tlist),
        limit=limit
    )
    cur.execute(query)
    sims = cur.fetchall()
    cur.close()
    con.close()

    graph_t = go.init_toric_graph(L)
    graph_l = go.init_toric_graph(L)

    for comp_id, created_on, seed in sims:

        time = created_on.strftime("%Y-%m-%d_%H-%M-%S")
        winner = "list" if ftree_tlist else "tree"
        name = f"L{L}_p{p}_{comp_id}_{time}_{seed}_{winner}"
        fileh = logging.FileHandler(f"./logs/{name}.log")
        formatter = logging.Formatter("%(message)s")
        fileh.setFormatter(formatter)
        log = logging.getLogger()  # root logger
        for hdlr in log.handlers[:]:  # remove all old handlers
            log.removeHandler(hdlr)
        log.addHandler(fileh)
        pr.printlog("\n______________________________________________________________________")
        pr.printlog(f"Sim computed by {comp_id} created on {created_on} with L = {L}, p = {p}")
        pr.printlog(f"Winner: {winner}")

        plot_both(graph_t, graph_l, seed, p, saveanim=None)
