from cposguf_run import sql_connection
from threshold_main import plot_thresholds

con, cur = sql_connection()


cur.execute("SELECT lattice, p, tot_sims, tree_sims, list_sims FROM cases")
data = cur.fetchall()
cur.close()
con.close()

fitL, fitp, fitN, fitt1, fitt2 = [], [], [], [], []
for L, p, N, t1, t2 in data:
    if N != 0:
        fitL.append(L)
        fitp.append(float(p))
        fitN.append(N)
        fitt1.append(t1)
        fitt2.append(t2)

uf0, uf1 = plot_thresholds(
    fitL, fitp, fitN, fitt1, plot_name="tree", modified_ansatz=1, data_select="even"
)
vf0, vf1 = plot_thresholds(
    fitL, fitp, fitN, fitt2, plot_name="list", modified_ansatz=1, data_select="even"
)
