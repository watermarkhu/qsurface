import pickling as pk
from threshold_main import plot_thresholds
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import pickling as pk


f, ax = plt.subplots()



def d0(): return {(0, "tree"): 0, (0, "list"): 0, (1, "tree"): 0, (1, "list"): 0}

type = "tree"
norm = 1

database = pk.load_obj(f"r1tl_threshold_p_norm{norm}")

data = [[] for i in range(4)]
L = [8 + 4*i for i in range(7)]
P = [(90 + 2*i)/1000 for i in range(11)]


for l in L:
    tnum = []
    for p in P:
        res = database[(l, p)]

        tree_succ = res[(1, 'tree')]
        tree_fail = res[(0, 'tree')]
        list_succ = res[(1, 'list')]
        list_fail = res[(0, 'list')]
        # tree_succ = res[(1, 0)]
        # tree_fail = res[(0, 0)]
        # list_succ = res[(1, 1)]
        # list_fail = res[(0, 1)]
        tot = tree_succ + tree_fail + list_succ + list_fail
        if type == "tree":
            if tree_succ != 0:
                data[0].append(l)
                data[1].append(p)
                data[2].append(tree_succ + tree_fail)
                data[3].append(tree_succ)
            tnum.append((list_succ + list_fail)/tot)
        elif type == "list":
            if list_succ != 0:
                data[0].append(l)
                data[1].append(p)
                data[2].append(list_succ + list_fail)
                data[3].append(list_succ)
            tnum.append((list_succ + list_fail)/tot)
        else:
            data[0].append(l)
            data[1].append(p)
            data[2].append(tot)
            data[3].append(tree_succ + list_succ)
            tnum.append(1)

    print(l, tnum)
    # ax0.plot(tnum)

plot_thresholds(*data, ax0 = ax, styles=[".", "-"], plot_name="")



# from cposguf_run import sql_connection
# con, cur = sql_connection()
# cur.execute("SELECT lattice, p, tot_sims, tree_sims, list_sims FROM cases")
# data = cur.fetchall()
# cur.close()
# con.close()
# fitL, fitp, fitN, fitt1, fitt2 = [], [], [], [], []
# for L, p, N, t1, t2 in data:
#     if N != 0:
#         fitL.append(L)
#         fitp.append(float(p))
#         fitN.append(N)
#         fitt1.append(t1)
#         fitt2.append(t2)
# plot_thresholds(fitL, fitp, fitN, fitt1, ax0=ax, styles=["x", ":"])
# le0 = Line2D([0], [0], ls=":", color="k")
# le1 = Line2D([0], [0], ls="--", color="k")
# leg1 = ax.legend()
# leg2 = ax.legend([le0, le1],["tree","r1tl_p_norm1_list"], loc='upper right')
# ax.add_artist(leg1)

plt.show()

# pk.save_obj(f, "fig_threshold_tree_vs_r1tl_p_norm1_list")
# f.savefig(f"r1tl_threshold_p_norm{norm}_{type}.pdf", transparent=True, format="pdf", bbox_inches="tight")
