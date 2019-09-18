import psycopg2 as pgs

ini = {'host': '34.77.14.37', 'port': '5432', 'database': 'cposguf', 'user': 'postgres', 'password': 'K5tm97HiKthh2ey7'}

con = pgs.connect(**ini)
con.set_session(autocommit=True)
cur = con.cursor()

L = [8 + 4*i for i in range(9)]
P = [i/1000 for i in [90 + i for i in range(21)]]
LP = [(l, p) for l in L for p in P]

for (l, p) in LP:
    cur.execute("INSERT INTO cases (lattice, p, target_tot_sims, target_diff_sims, target_ubuck_wins, target_vcomb_wins, tot_sims, diff_sims, ubuck_wins, vcomb_wins) VALUES ({}, {}, 300000, 100000, 50000, 50000, 0, 0, 0, 0)".format(l, p))
cur.close()
con.close()
