import psycopg2 as pgs
from cposguf import read_config

p = None
L = None

comp_id, num_process, iters, sql_config = read_config("./cposguf.ini")
con = pgs.connect(**sql_config)
con.set_session(autocommit=True)
cur = con.cursor()
