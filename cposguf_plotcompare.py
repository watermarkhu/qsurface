from cposguf_run import sql_connection, input_error_array, fetch_query
import graph_objects as go
import toric_code as tc
import toric_plot as tp
import unionfind_tree as uf
import uf_plot as up
from matplotlib import pyplot as plt
from matplotlib.lines import Line2D



def grow_clusters(graph_u, uf_plot_u, graph_v, uf_plot_v, plot_step=0, print_steps=0, random_traverse=0):

    '''
    Grows the clusters, and merges them until there are no uneven clusters left.
    Starting from the lowest bucket, clusters are popped from the list and grown with {grow_cluster}. Due to the nature of how clusters are appended to the buckets, a cluster needs to be checked for 1) root level 2) bucket level and 3) parity before it can be grown.

    '''

    for bucket_i, (bucket_u, bucket_v) in enumerate(zip(graph_u.buckets, graph_v.buckets)):


        if bucket_i > max([graph_u.maxbucket, graph_v.maxbucket]): break

        if bucket_u == [] and bucket_v == []: continue

        if print_steps:
            print("############################ GROW ############################")
            print("UBUCK: Growing bucket", bucket_i, "of", graph_u.maxbucket, ":", bucket_u)
            print("Remaining buckets:", graph_u.buckets[bucket_i+1:graph_u.maxbucket+1], graph_u.wastebasket)
            uf_plot_u.waitforkeypress()

        while bucket_u != []:                          # Loop over all clusters in the current bucket\
            cluster = bucket_u.pop()
            root_cluster = uf.find_cluster_root(cluster)
            if root_cluster.bucket == bucket_i:
                if print_steps: graph_u.print_graph_stop([root_cluster], prestring="B: ")
                uf.grow_full(graph_u, root_cluster, root_cluster, root_cluster.support, uf_plot_u, plot_step, print_steps, 0, random_traverse, vcomb=0)
            else:
                if print_steps:
                    if root_cluster.bucket is None:
                        print(root_cluster, "is even.\n")
                    else:
                        if root_cluster.bucket > graph_u.maxbucket:
                            print(root_cluster, "is already in the wastebasket\n")
                        else:
                            print(root_cluster, "is already in another bucket.\n")
        if print_steps: graph_u.print_graph_stop(prestring="UBUCK ", printmerged=0)


        if print_steps:
            print("############################ GROW ############################")
            print("VCOMB: Growing bucket", bucket_i, "of", graph_v.maxbucket, ":", bucket_v)
            print("Remaining buckets:", graph_v.buckets[bucket_i+1:graph_v.maxbucket+1], graph_v.wastebasket)
            uf_plot_v.waitforkeypress()

        while bucket_v != []:                          # Loop over all clusters in the current bucket\
            cluster = bucket_v.pop()
            root_cluster = uf.find_cluster_root(cluster)
            if root_cluster.bucket == bucket_i:
                if print_steps: graph_v.print_graph_stop([root_cluster], prestring="B: ")
                uf.grow_full(graph_v, root_cluster, root_cluster, root_cluster.support, uf_plot_v, plot_step, print_steps, 0, random_traverse, vcomb=1)
            else:
                if print_steps:
                    if root_cluster.bucket is None:
                        print(root_cluster, "is even.\n")
                    else:
                        if root_cluster.bucket > graph_v.maxbucket:
                            print(root_cluster, "is already in the wastebasket\n")
                        else:
                            print(root_cluster, "is already in another bucket.\n")

        if print_steps: graph_v.print_graph_stop(prestring="VCOMB ", printmerged=0)

        if not plot_step:
            txt = "" if print_steps else "Growing bucket #" + str(bucket_i) + "/" + str(max([graph_u.maxbucket, graph_v.maxbucket])) + "."
            uf_plot_u.draw_plot(txt)
            uf_plot_v.draw_plot("")

    uf_plot_u.waitforkeypress("Clusters grown.")


def plot_final(tp, graph_u, graph_v):
    '''
    param: flips        qubits that have flipped in value (y,x)
    param: arrays       data array of the (corrected) qubit states
    plots the applied stabilizer measurements over the lattices
    also, in the qubits that have flipped in value a smaller white circle is plotted

    optionally, the axis is clear and the final state of the lattice is plotted
    '''

    plt.sca(tp.ax)

    uc, vc, wc = [.2, 0, .8], [.2, .8, 0], [.2, .8, .8]

    for y in range(tp.size):
        for x in range(tp.size):
            for td in range(2):
                u_error = graph_u.E[(0, y, x, td)].matching
                v_error = graph_v.E[(0, y, x, td)].matching

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

    uerr = Line2D([0], [0], lw=0, marker='o', color=uc, mfc='w', mew=2, ms=10, label='UBUCK')
    verr = Line2D([0], [0], lw=0, marker='o', color=vc, mfc='w', mew=2, ms=10, label='VCOMB')
    werr = Line2D([0], [0], lw=0, marker='o', color=wc, mfc='w', mew=2, ms=10, label='U&V')

    legend1 = plt.legend(handles=[uerr, verr, werr], bbox_to_anchor=(1.15, 0.95), loc="upper right", ncol=1)
    tp.ax.add_artist(legend1)

    tp.canvas.blit(tp.ax.bbox)
    tp.waitforkeypress("Corrections plotted.")


def plot_both(graph_u, graph_v, array):

    toric_plot = tp.lattice_plot(graph_u, plot_size=10, line_width=2)

    input_error_array(graph_u, array)
    input_error_array(graph_v, array)
    toric_plot.plot_errors()
    # Measure stabiliziers
    tc.measure_stab(graph_u, toric_plot)
    tc.measure_stab(graph_v)

    # Peeling decoder
    uf_plot_u = up.toric(graph_u, toric_plot.f, axn=2, plot_size=10, line_width=1.5, plotstep_click=1)
    uf_plot_v = up.toric(graph_v, toric_plot.f, axn=3, plot_size=10, line_width=1.5, plotstep_click=1)

    axes = toric_plot.f.get_axes()
    axes[0].set_title("Peeling lattice")
    axes[1].set_title("UBUCK peeling lattice")
    axes[2].set_title("VCOMB peeling lattice")

    uf.find_clusters(graph_u, uf_plot=uf_plot_u, plot_step=0, vcomb=0)
    uf.find_clusters(graph_v, uf_plot=uf_plot_v, plot_step=0, vcomb=1)

    grow_clusters(graph_u, uf_plot_u, graph_v, uf_plot_v, plot_step=0, print_steps=1)

    uf.peel_clusters(graph_u, uf_plot=uf_plot_u, plot_step=0)
    uf.peel_clusters(graph_v, uf_plot=uf_plot_v, plot_step=0)

    # Apply matching
    tc.apply_matching_peeling(graph_u)
    tc.apply_matching_peeling(graph_v)

    plot_final(toric_plot, graph_u, graph_v)

    # Measure logical operator
    graph_u.reset()
    graph_v.reset()


if __name__ == "__main__":

    L = 12
    p = 0.09
    limit = 10
    type = "vcomb"

    con, cur = sql_connection()
    query =  fetch_query("*", p=p, L=L, type=type, limit=limit)
    cur.execute(query)
    sims = cur.fetchall()
    cur.close()
    con.close()

    graph_u = go.init_toric_graph(L)
    graph_v = go.init_toric_graph(L)

    for _, _, _, comp_id, created_on, ubuck_win, _, array in sims:

        print("Displaying sim by", comp_id, "created on", created_on)
        winner = "UBUCK" if ubuck_win else "VCOMB"
        print("Winner:", winner)

        plot_both(graph_u, graph_v, array)
