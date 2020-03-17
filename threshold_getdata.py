import pandas as pd
from threshold_batchsql import connect_database
from progiter import ProgIter
import os


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


if __name__ == "__main__":

    import argparse
    from oopsc import add_kwargs

    parser = argparse.ArgumentParser(
        prog="mysql datagetter",
        description="saves a mysql database",
    )

    kwargs = [
        ["-d", "--database", "store", "name of database", dict(type=str, metavar="")],
        ["-f", "--folder", "store", "folder of csv files", dict(type=str, metavar="")],
        ["-o", "--output", "store", "output, needs to add file ex.", dict(type=str, metavar="")],
    ]

    add_kwargs(parser, kwargs)

    args=vars(parser.parse_args())
    get_data(**args)
