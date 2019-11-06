from cposguf_run import sql_connection, input_error_array, fetch_query
import graph_objects as go
import toric_code as tc
import toric_error as te
import toric_plot as tp
import unionfind as uf
import unionfind_list as ufl
import unionfind_tree as uft
import uf_plot as up
from matplotlib import pyplot as plt
from matplotlib.lines import Line2D


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
        [0], [0], lw=0, marker="o", color=uc, mfc="w", mew=2, ms=10, label="UBUCK"
    )
    verr = Line2D(
        [0], [0], lw=0, marker="o", color=vc, mfc="w", mew=2, ms=10, label="VCOMB"
    )
    werr = Line2D(
        [0], [0], lw=0, marker="o", color=wc, mfc="w", mew=2, ms=10, label="U&V"
    )

    legend1 = plt.legend(
        handles=[uerr, verr, werr],
        bbox_to_anchor=(1.15, 0.95),
        loc="upper right",
        ncol=1,
    )
    tp.ax.add_artist(legend1)

    tp.canvas.blit(tp.ax.bbox)
    tp.waitforkeypress("Corrections plotted.")


def plot_both(graph_t, graph_l, seed, p):

    toric_plot = tp.lattice_plot(graph_t, plot_size=6, line_width=2)

    te.apply_random_seed(seed)
    te.init_pauli(graph_t, pX=float(p))
    toric_plot.plot_errors()
    tc.measure_stab(graph_t, toric_plot)
    uf_plot_t = up.toric(
        graph_t, toric_plot.f, axn=2, plot_size=10, line_width=1.5, plotstep_click=1
    )
    axes = toric_plot.f.get_axes()
    axes[0].set_title("Peeling lattice")
    axes[1].set_title("tree peeling lattice")

    uf.find_clusters(graph_t, uf_plot=uf_plot_t, plot_step=0, vcomb=0)
    uft.grow_clusters(graph_t, uf_plot_t, plot_step=0)
    uf.peel_clusters(graph_t, uf_plot=uf_plot_t, plot_step=0)
    tc.apply_matching_peeling(graph_t)

    te.apply_random_seed(seed)
    te.init_pauli(graph_l, pX=float(p))
    toric_plot.plot_errors()
    tc.measure_stab(graph_l)
    uf_plot_l = up.toric(
        graph_l, toric_plot.f, axn=3, plot_size=10, line_width=1.5, plotstep_click=1
    )
    axes = toric_plot.f.get_axes()
    axes[2].set_title("list peeling lattice")
    uf.find_clusters(graph_l, uf_plot=uf_plot_l, plot_step=0, vcomb=1)
    ufl.grow_clusters(graph_l, uf_plot_l, plot_step=0)
    uf.peel_clusters(graph_l, uf_plot=uf_plot_l, plot_step=0)
    tc.apply_matching_peeling(graph_l)

    plot_final(toric_plot, graph_t, graph_l)

    # Measure logical operator
    graph_t.reset()
    graph_l.reset()


if __name__ == "__main__":

    L = 8
    p = 0.091
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

    sims[3][2]

    graph_t = go.init_toric_graph(L)
    graph_l = go.init_toric_graph(L)

    for comp_id, created_on, seed in sims:

        print("Displaying sim by", comp_id, "created on", created_on)
        winner = "list" if ftree_tlist else "tree"
        print("Winner:", winner)

        plot_both(graph_t, graph_l, seed, p)
