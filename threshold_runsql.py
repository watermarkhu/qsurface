'''
2020 Mark Shui Hu, QuTech

www.github.com/watermarkhu/oop_surface_code
_____________________________________________

'''

import oopsc
import numpy as np
import pandas as pd
import git, sys, os
import sqlalchemy


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


def run_thresholds(
        decoder,
        sql_database,
        batchnumber,
        lattice_type="toric",
        lattices = [],
        perror = [],
        iters = 0,
        measurement_error=False,
        modified_ansatz=False,
        save_result=True,
        file_name="thres",
        show_plot=False,
        plot_title=None,
        folder = "./",
        P_store=1000,
        debug=False,
        **kwargs
        ):
    '''
    ############################################
    '''

    if measurement_error:
        import graph_3D as go
    else:
        import graph_2D as go

    sys.setrecursionlimit(100000)
    r = git.Repo(os.path.dirname(__file__))
    full_name = r.git.rev_parse(r.head, short=True) + f"_{lattice_type}_{go.__name__}_{decoder.__name__}_{file_name}"
    if not plot_title:
        plot_title = full_name


    if not os.path.exists(folder):
        os.makedirs(folder)

    if kwargs.pop("subfolder"):
        os.makedirs(folder + "/data/", exist_ok=True)
        os.makedirs(folder + "/figures/", exist_ok=True)
        file_path = folder + "/data/" + full_name + ".csv"
        # fig_path = folder + "/figures/" + full_name + ".pdf"
    else:
        file_path = folder + "/" + full_name + ".csv"
        # fig_path = folder + "/" + full_name + ".pdf"

    progressbar = kwargs.pop("progressbar")

    data = None
    int_P = [int(p*P_store) for p in perror]
    config = oopsc.default_config(**kwargs)

    table = "t_{}".format(batchnumber)
    con = connect_database(sql_database)
    create_table(con, table)

    # Simulate and save results to file
    for lati in lattices:


        graph = oopsc.lattice_type(lattice_type, config, decoder, go, lati)

        for pi, int_p in zip(perror, int_P):

            if check_row_exists(con, table, lati, pi):
                continue

            print("Calculating for L = ", str(lati), "and p =", str(pi))

            oopsc_args = dict(
                paulix=pi,
                lattice_type=lattice_type,
                debug=debug,
                progressbar=progressbar
            )
            if measurement_error:
                oopsc_args.update(measurex=pi)
            output = oopsc.multiple(lati, config, iters, graph=graph, worker=batchnumber, **oopsc_args)

            sql_data = dict(L=lati, p=pi, **output)
            insert_database(con, table, sql_data)

            if data is None:
                if os.path.exists(file_path):
                    data = pd.read_csv(file_path, header=0)
                    data = data.set_index(["L", "p"])
                else:
                    columns = list(output.keys())
                    index = pd.MultiIndex.from_product([lattices, int_P], names=["L", "p"])
                    data = pd.DataFrame(
                        np.zeros((len(lattices) * len(perror), len(columns))), index=index, columns=columns
                    )

            if data.index.isin([(lati, int_p)]).any():
                for key, value in output.items():
                    data.loc[(lati, int_p), key] += value
            else:
                for key, value in output.items():
                    data.loc[(lati, int_p), key] = value

            data = data.sort_index()
            if save_result:
                data.to_csv(file_path)

    con.close()


if __name__ == "__main__":

    import argparse
    from oopsc import add_args

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

    parser.add_argument("batchnumber",
        action="store",
        type=int,
        help="batch number",
        metavar="batch",
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
        ["-s", "--save_result", "store_true", "save results - toggle", dict()],
        ["-sp", "--show_plot", "store_true", "show plot - toggle", dict()],
        ["-fn", "--file_name", "store", "plot filename - toggle", dict(default="thres", metavar="")],
        ["-pt", "--plot_title", "store", "plot filename - toggle", dict(default="", metavar="")],
        ["-f", "--folder", "store", "base folder path - toggle", dict(default="./", metavar="")],
        ["-sf", "--subfolder", "store_true", "store figures and data in subfolders - toggle", dict()],
        ["-pb", "--progressbar", "store_true", "enable progressbar - toggle", dict()],
        ["-dgc", "--dg_connections", "store_true", "use dg_connections pre-union processing - toggle", dict()],
        ["-dg", "--directed_graph", "store_true", "use directed graph for evengrow - toggle", dict()],
        ["-db", "--debug", "store_true", "enable debugging hearistics - toggle", dict()],
    ]

    add_args(parser, pos_arguments, "positional", "range of L and p values")
    add_args(parser, key_arguments)


    args=vars(parser.parse_args())
    decoder = args.pop("decoder")
    batchnumber = args.pop("batchnumber")
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


    run_thresholds(decode, sql_database, batchnumber, **args)
