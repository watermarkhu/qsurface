from cposguf_run import sql_connection
from threshold_main import plot_thresholds

con, cur = sql_connection()


cur.execute("SELECT lattice, p, tot_sims, ubuck_sims, vcomb_sims FROM cases")
data = cur.fetchall()
cur.close()
con.close()

fitL, fitp, fitN, ufitt, vfitt = [], [], [], [], []
for L, p, N, ut, vt in data:
    if N != 0:
        fitL.append(L)
        fitp.append(float(p))
        fitN.append(N)
        ufitt.append(ut)
        vfitt.append(vt)

uf0, uf1 = plot_thresholds(fitL, fitp, fitN, ufitt, plot_name="ubuck", modified_ansatz=0, data_select="even")
vf0, vf1 = plot_thresholds(fitL, fitp, fitN, vfitt, plot_name="vcomb", modified_ansatz=0, data_select="even")
