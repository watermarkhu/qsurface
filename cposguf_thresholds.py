from cposguf_run import sql_connection
from threshold_main import plot_thresholds

con, cur = sql_connection()


cur.execute("SELECT lattice, p, tot_sims, ubuck_sims, vcomb_sims FROM cases")
data = cur.fetchall()
cur.close()
con.close()

fitL, fitp, fitN, ufitt, vfitt = map(list, zip(*data))
fitp = [float(p) for p in fitp]

uf0, uf1 = plot_thresholds(fitL, fitp, fitN, ufitt, plot_name="ubuck")
vf0, vf1 = plot_thresholds(fitL, fitp, fitN, vfitt, plot_name="vcomb")
