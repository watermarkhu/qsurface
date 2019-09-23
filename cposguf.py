import graph_objects as go
import toric_code as tc
import toric_error as te
import unionfind_tree as uf
import multiprocessing as mp
from progiter import ProgIter
import psycopg2 as pgs
from psycopg2 import extras as pgse
from configparser import ConfigParser
import random
import time
import cpuinfo



def add_new_sim(cursor, comp_id, lattice, p, ubuck, vcomb, array):
    query = "INSERT INTO simulations (lattice, p, comp_id, created_on, ubuck_solved, vcomb_solved, error_data) VALUES ({0}, {1}, '{2}', current_timestamp, {3}, {4}, ARRAY{5});".format(lattice, p, comp_id, ubuck, vcomb, array)
    cursor.execute(query)


def add_new_comp(cursor, id, cputype):
    query = "INSERT INTO computers (comp_id, cpu_type) VALUES ('" + id + "', '" + cputype + "');"
    cursor.execute(query)


def read_config(path):
    cp = ConfigParser()
    cp.read(path)
    sql_config = {}
    comp_id = cp.get('config', 'comp_id')
    num_process = cp.getint('config', 'num_process')
    iters = cp.getint('config', 'iters')
    names = ['host', 'port', 'database', 'user', 'password', 'sslmode', 'sslrootcert', 'sslcert', 'sslkey']
    for name in names:
        sql_config[name] = cp.get('sql_database', name)
    return comp_id, num_process, iters, sql_config


def output_error_array(graph):
    array = [[], [], []]
    for edge in graph.E.values():
        if edge.state:
            array[0].append(edge.qID[1])
            array[1].append(edge.qID[2])
            array[2].append(edge.qID[3])
    return array


def input_error_array(graph, array):
    for y, x, td in list(map(list, zip(*array))):
        graph.E[(0, int(y), int(x), int(td))].state = 1


def multiple(ini, comp_id, iters, size, p, worker=None):

    def single(graph):
        te.init_pauli(graph, pX=p, worker=worker)           # Simulate for unique bucket method
        array = output_error_array(graph)
        tc.measure_stab(graph)
        uf.find_clusters(graph)
        uf.grow_clusters(graph)
        uf.peel_clusters(graph)
        tc.apply_matching_peeling(graph)
        logical_error = tc.logical_error(graph)
        graph.reset()
        ubuck_win = True if logical_error == [False, False, False, False] else False

        input_error_array(graph, array)                     # Simulate for vertical combined method
        tc.measure_stab(graph)
        uf.find_clusters(graph, vcomb=1)
        uf.grow_clusters(graph, vcomb=1)
        uf.peel_clusters(graph)
        tc.apply_matching_peeling(graph)
        logical_error = tc.logical_error(graph)
        graph.reset()
        vcomb_win = True if logical_error == [False, False, False, False] else False

        return (ubuck_win, vcomb_win, array)

    # Open SQL connection
    con = pgs.connect(**ini)
    con.set_session(autocommit=True)
    cur = con.cursor()

    # Simulate
    graph = go.init_toric_graph(size)
    results = [single(graph) for _ in ProgIter(range(iters))]
    diff_res = [result for result in results if result[0] != result [1]]

    # Insert simulation into database
    query = "INSERT INTO simulations (lattice, p, comp_id, created_on, ubuck_solved, vcomb_solved, error_data) VALUES %s "
    template = "(" + str(size) + ", " + str(p) + ", '" + str(comp_id) + "', current_timestamp, %s, %s, %s)"
    pgse.execute_values(cur, query, diff_res, template)

    # Update cases counters
    cur.execute("SELECT tot_sims, diff_sims, ubuck_wins, vcomb_wins FROM cases WHERE lattice = {} AND p = {}".format(size, p))
    counter = list(cur.fetchone())
    counter[0] += iters
    for ubuck_win, vcomb_win, _ in results:
        if ubuck_win != vcomb_win:
            counter[1] += 1
        if ubuck_win and not vcomb_win:
            counter[2] += 1
        if not ubuck_win and vcomb_win:
            counter[3] += 1

    cur.execute("UPDATE cases SET tot_sims = {}, diff_sims = {}, ubuck_wins = {}, vcomb_wins = {} WHERE lattice = {} and p = {}".format(*counter, size, p))

    cur.close()
    con.close()


def multiprocess(ini, comp_id, iters, size, p, processes=None):

    if processes is None:
        processes = mp.cpu_count()

    process_iters = iters//processes
    rest_iters = iters - process_iters*processes
    workers = []

    for i in range(processes-1):
        workers.append(mp.Process(target=multiple, args=(ini, comp_id, process_iters, size, p, i)))
    workers.append(mp.Process(target=multiple, args=(ini, comp_id, process_iters + rest_iters, size, p, processes - 1)))


    for worker in workers:
        worker.start()
    print("Started", processes, "workers.")
    for worker in workers:
        while worker.is_alive():
            time.sleep(1)
        worker.join()


if __name__ == '__main__':

    comp_id, num_process, iters, sql_config = read_config("./cposguf.ini")

    con = pgs.connect(**sql_config)
    con.set_session(autocommit=True)
    cur = con.cursor()

    # Check computer listing
    cur.execute("SELECT comp_id FROM computers")
    computers = cur.fetchall()
    if comp_id not in [c[0] for c in computers]:
        cputype = cpuinfo.get_cpu_info()['brand']
        add_new_comp(cur, comp_id, cputype)

    running = True
    while True:

        # Choose case
        cur.execute("SELECT lattice,p FROM cases_open_free")
        options = cur.fetchall()
        if len(options) == 0:
            cur.execute("SELECT lattice,p FROM cases_open")
            options = cur.fetchall()
            if len(options) == 0:
                exit()
        lattice, deci_p = random.choice(options)
        p = float(deci_p)
        print("Selected lattice = {}, p = {}".format(lattice, p))

        # Set computer active case and simulate
        cur.execute("UPDATE computers SET active_lattice = {}, active_p = {} WHERE comp_id = '{}'".format(lattice, p, comp_id))
        if num_process == 1:
            multiple(sql_config, comp_id, iters, lattice, p)
        else:
            multiprocess(sql_config, comp_id, iters, lattice, p, num_process)

        # Check if keep running
        cur.execute("SELECT active_lattice, active_p FROM computers WHERE comp_id = '{}'".format(comp_id))
        if cur.fetchone() == (None, None):
            print("Stopped by user by database null entry")
            break

    cur.close()
    con.close()
