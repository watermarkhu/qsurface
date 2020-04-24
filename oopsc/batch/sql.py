'''
2020 Mark Shui Hu, QuTech

www.github.com/watermarkhu/oop_surface_code
_____________________________________________

'''
import os, sqlalchemy
import pandas as pd
from progiter import ProgIter


def writeline(path, worker, line, type="a"):
    file = f"{path}{worker}.csv"
    if type == "w" and os.path.isfile(file):
        return
    f = open(file, type)
    f.write(line + "\n")
    f.close()


def get_columns():
    columns = [
        "L",
        "p",
        "N",
        "succes",
        "weight_m",
        "weight_v",
        "time_m",
        "time_v",
        "gbu_m",
        "gbu_v",
        "gbo_m",
        "gbo_v",
        "ufu_m",
        "ufu_v",
        "uff_m",
        "uff_v",
        "mac_m",
        "mac_v",
        "ctd_m",
        "ctd_v",
    ]
    return columns


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


def meanvarunion(key, orow, ovalue, oN, irow, ivalue, iN):
    if key[-2:] == "_m":
        ovalue = (ovalue*oN + ivalue*iN)/(oN + iN)
    elif key[-2:] == "_v":
        mkey = key[:-2] + "_m"
        pmean, cmean = orow[mkey], irow[mkey]
        mean = (pmean*oN + cmean*iN)/(oN + iN)
        ovalue = ((ovalue+(pmean-mean)**2)*oN + (ivalue+(cmean-mean)**2)*iN)/(oN + iN)
    else:
        ovalue += ivalue
    return ovalue


def get_data(database, folder, output):

    data = []

    if database is not None:
        con = connect_database(database)
        res = con.execute('SHOW TABLES')
        tables = res.fetchall()

        print("reading sql data...")
        for table in ProgIter(tables):
            data.append(pd.read_sql_table(table[0], con).drop(["id"], axis=1).set_index(["L", "p"]))
        con.close()

    if folder is not None:
        onlyfiles = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]

        print("reading local data...")
        for file_path in ProgIter(onlyfiles):
            path = folder + file_path
            try:
                df = pd.read_csv(path, header=0)
                data.append(df.set_index(["L", "p"]))
            except:
                print("cound not read {}".format(path))

    odata = pd.DataFrame(columns=list(data[0].index.names) + list(data[0].columns)).set_index(["L", "p"])

    print("processing data...")
    for idata in ProgIter(data):
        for index, irow in idata.iterrows():

            index = (index[0], f"{index[1]:.6f}")
            if index not in odata.index:
                irow.name = index
                odata = odata.append(irow)
            else:
                orow = odata.loc[index]
                iN, oN = irow["N"], orow["N"]

                for (key, ovalue) in orow.items():
                    if len(irow.shape) == 2:
                        for _, row in irow.iterrows():
                            ivalue = row.loc[key]
                            ovalue = meanvarunion(key, orow, ovalue, oN, irow, ivalue, iN)

                    else:
                        ivalue = irow.loc[key]
                        ovalue = meanvarunion(key, orow, ovalue, oN, irow, ivalue, iN)

                    odata.loc[index, key] = ovalue

    print(odata)

    if output is not None:
        print("saving data...")
        odata = odata.sort_index()
        odata.to_csv(output)
