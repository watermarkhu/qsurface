'''
2020 Mark Shui Hu, QuTech

www.github.com/watermarkhu/oop_surface_code
_____________________________________________

'''

import sys
import sqlalchemy
import multiprocessing as mp

def connect_database(database):
    database_username = 'root'
    database_password = 'Guess20.Located.Oil...'
    database_ip       = '104.199.14.242'
    database_name     = database
    database_connection = sqlalchemy.create_engine('mysql+pymysql://{0}:{1}@{2}/{3}'.format(database_username, database_password, database_ip, database_name))
    return database_connection.connect()


def create_table(con, table_name):
    create_table = (
        "CREATE TABLE IF NOT EXISTS `{}` ("
        "`id` int NOT NULL AUTO_INCREMENT,"
        "`L` int NOT NULL,"
        "`p` decimal(6,6) NOT NULL,"
        "`N` int NOT NULL,"
        "`succes` int NOT NULL,"
        "`weight_m` float NOT NULL,"
        "`weight_v` float NOT NULL,"
        "`time_m` float NOT NULL,"
        "`time_v` float NOT NULL,"
        "`gbu_m` float NOT NULL,"
        "`gbu_v` float NOT NULL,"
        "`gbo_m` float NOT NULL,"
        "`gbo_v` float NOT NULL,"
        "`ufu_m` float NOT NULL,"
        "`ufu_v` float NOT NULL,"
        "`uff_m` float NOT NULL,"
        "`uff_v` float NOT NULL,"
        "`mac_m` float NOT NULL,"
        "`mac_v` float NOT NULL,"
        "`ctd_m` float NOT NULL,"
        "`ctd_v` float NOT NULL,"
        " PRIMARY KEY (`id`)"
        ")".format(table_name)
    )
    trans = con.begin()
    con.execute(create_table)
    trans.commit()


def insert_database(con, table_name, data):
    columns = ', '.join("`{}`".format(s) for s in data)
    values = ', '.join(str(s) for s in data.values())
    query = "INSERT INTO `{}` ({}) VALUES ({}) ".format(table_name, columns, values)
    trans = con.begin()
    con.execute(query)
    trans.commit()


def check_row_exists(con, tablename, L, p):
    query = f"SELECT 1 FROM {tablename} WHERE L = {L} AND p = {p}"
    result = con.execute(query)
    row = result.fetchall()
    return bool(row)


def multiple(
    sql_database,
    graph,
    size,
    config,
    iters,
    paulix=0,
    worker=0,
    debug=True,
    **kwargs
):
    from simulator import init_random_seed, single, get_mean_var
    from decorators import debug as db


    """
    Runs the peeling decoder for a number of iterations. The graph is reused for speedup.
    """
    table = f"N{worker}"

    con = connect_database(sql_database)

    if check_row_exists(con, table, size, paulix):
        con.close()
        return
    else:
        con.close()


    seeds = [init_random_seed(worker=worker, iteration=iter) for iter in range(iters)]

    options = dict(
        graph=graph,
        worker=worker,
        called=0,
        debug=True,
    )

    zipped = zip(range(iters), seeds)
    result = [single(size, config, paulix=paulix, iter=iter, seed=seed, **options, **kwargs) for iter, seed in zipped]

    output = dict(
        N       = iters,
        succes  = sum(result)
    )
    if debug:
        output.update(**get_mean_var(graph.matching_weight, "weight"))
        for key, value in graph.decoder.clist.items():
            output.update(**get_mean_var(value, key))
        db.reset_counters(graph)

    sql_data = dict(L=size, p=paulix, **output)

    con = connect_database(sql_database)
    insert_database(con, table, sql_data)
    con.close()


def multiprocess(
        sql_database,
        graph,
        size,
        config,
        iters,
        processes,
        node=0,
        **kwargs
    ):
    """
    Runs the peeling decoder for a number of iterations, split over a number of processes
    """

    process_iters = iters // processes
    workers = []

    for i, g in enumerate(graph, int(node*processes)):
        workers.append(
            mp.Process(
                target=multiple,
                args=(sql_database, g, size, config, process_iters),
                kwargs=dict(worker=i, **kwargs),
            )
        )
    print("Starting", processes, "workers.")

    for worker in workers:
        worker.start()

    for worker in workers:
        worker.join()


def run_thresholds(
        decoder,
        sql_database,
        node=0,
        lattice_type="toric",
        lattices = [],
        perror = [],
        iters = 0,
        processes=1,
        measurement_error=False,
        P_store=1000,
        debug=False,
        **kwargs
        ):
    '''
    ############################################
    '''

    import oopsc

    if measurement_error:
        import graph_3D as go
    else:
        import graph_2D as go

    sys.setrecursionlimit(100000)

    progressbar = kwargs.pop("progressbar")

    int_P = [int(p*P_store) for p in perror]
    config = oopsc.default_config(**kwargs)

    con = connect_database(sql_database)
    for i in range(processes):
        p = i + node*processes
        create_table(con, f"N{p}")
        con.close()


    # Simulate and save results to file
    for lati in lattices:

        graph = [oopsc.lattice_type(lattice_type, config, decoder, go, lati) for _ in range(processes)]

        for pi, int_p in zip(perror, int_P):

            print("Calculating for L = ", str(lati), "and p =", str(pi))

            oopsc_args = dict(
                paulix=pi,
                lattice_type=lattice_type,
                debug=debug,
                progressbar=progressbar
            )
            if measurement_error:
                oopsc_args.update(measurex=pi)

            multiprocess(sql_database, graph, lati, config, iters, processes, node, **oopsc_args)




if __name__ == "__main__":

    import argparse
    from simulator import add_kwargs

    parser = argparse.ArgumentParser(
        prog="threshold_run",
        description="run a threshold computation",
        usage='%(prog)s [-h/--help] decoder lattice_type iters -l [..] -p [..] (lattice_size)'
    )

    parser.add_argument("sql_database",
        action="store",
        type=str,
        help="sql database name",
        metavar="sql",
    )

    parser.add_argument("node",
        action="store",
        type=int,
        help="node number",
        metavar="node",
    )

    parser.add_argument("processes",
        action="store",
        type=int,
        help="number of processes",
        metavar="processes",
    )

    parser.add_argument("decoder",
        action="store",
        type=str,
        help="type of decoder - {mwpm/uf/eg}",
        metavar="d",
    )

    parser.add_argument("lattice_type",
        action="store",
        type=str,
        help="type of lattice - {toric/planar}",
        metavar="lt",
    )

    parser.add_argument("iters",
        action="store",
        type=int,
        help="number of iterations - int",
        metavar="i",
    )

    pos_arguments= [
        ["-l", "--lattices", "store", "lattice sizes - verbose list int", dict(type=int, nargs='*', metavar="", required=True)],
        ["-p", "--perror", "store", "error rates - verbose list float", dict(type=float, nargs='*', metavar="", required=True)],
    ]

    key_arguments = [
        ["-me", "--measurement_error", "store_true", "enable measurement error (2+1D) - toggle", dict()],
        ["-ma", "--modified_ansatz", "store_true", "use modified ansatz - toggle", dict()],
        ["-pb", "--progressbar", "store_true", "enable progressbar - toggle", dict()],
        ["-dgc", "--dg_connections", "store_true", "use dg_connections pre-union processing - toggle", dict()],
        ["-dg", "--directed_graph", "store_true", "use directed graph for evengrow - toggle", dict()],
        ["-db", "--debug", "store_true", "enable debugging hearistics - toggle", dict()],
    ]

    add_kwargs(parser, pos_arguments, "positional", "range of L and p values")
    add_kwargs(parser, key_arguments)


    args=vars(parser.parse_args())
    decoder = args.pop("decoder")
    sql_database = args.pop("sql_database")


    if decoder == "mwpm":
        import mwpm as decode
        print(f"{'_'*75}\n\ndecoder type: minimum weight perfect matching (blossom5)")
    elif decoder == "uf":
        import unionfind as decode
        print(f"{'_'*75}\n\ndecoder type: unionfind")
        if args["dg_connections"]:
            print(f"{'_'*75}\n\nusing dg_connections pre-union processing")
    elif decoder == "eg":
        import unionfind_eg as decode
        print("{}\n\ndecoder type: unionfind evengrow with {} graph".format("_"*75,"directed" if args["directed_graph"] else "undirected"))
        if args["dg_connections"]:
            print(f"{'_'*75}\n\nusing dg_connections pre-union processing")


    run_thresholds(decode, sql_database, **args)
