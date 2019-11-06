from cposguf_run import sql_connection

con, cur = sql_connection()

L = [8 + 4 * i for i in range(10)]
P = [i / 1000 for i in [90 + i for i in range(21)]]

LP = [(l, p) for l in L for p in P]

for (l, p) in LP:
    cur.execute(
        "INSERT INTO cases (lattice, p, target_tot_sims, target_tree_wins, target_list_wins, tot_sims, tree_sims, list_sims, tree_wins, list_wins) VALUES ({}, {}, 1000000, 20000, 20000, 0, 0, 0, 0, 0)".format(
            l, p
        )
    )
cur.close()
con.close()
