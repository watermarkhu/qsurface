import pandas as pd
from threshold_runsql import connect_database
from progiter import ProgIter

database = "eg_planar_3d_test"

def get_data(database, output):

    con = connect_database(database)
    res = con.execute('SHOW TABLES')
    tables = res.fetchall()

    print("reading data...")
    data = []
    for table in ProgIter(tables):
        data.append(pd.read_sql_table(table[0], con).drop(["id"], axis=1).set_index(["L", "p"]))

    cdata = data[0]

    print("processing data...")
    for i in ProgIter(range(1, len(tables))):
        pdata = data[i]

        for j in range(len(pdata)):
            prow = pdata.iloc[j,:]
            if prow.name not in cdata.index:
                cdata = cdata.append(prow)
            else:
                crow = cdata.loc[prow.name]
                cN, pN = crow["N"], prow["N"]

                for (key, pvalue), cvalue in zip(prow.items(), crow):

                    if key[-2:] == "_m":
                        cdata.loc[prow.name, key] = (pvalue*pN + cvalue*cN)/(pN + cN)
                    elif key[-2:] == "_v":
                        mkey = key[:-2] + "_m"
                        pmean, cmean = prow[mkey], crow[mkey]
                        mean = cdata.loc[prow.name, mkey]
                        cdata.loc[prow.name, key] = ((pvalue+(pmean-mean)**2)*pN + (cvalue+(cmean-mean)**2)*cN)/(pN + cN)
                    else:
                        cdata.loc[prow.name, key] = pvalue + cvalue

    print("saving data...")
    cdata = cdata.sort_index()
    cdata.to_csv(output)


if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(
        prog="mysql datagetter",
        description="saves a mysql database",
    )

    parser.add_argument("database",
        action="store",
        type=str,
        help="name of database",
        metavar="dn",
    )

    parser.add_argument("output",
        action="store",
        type=str,
        help="output, needs to add file ex.",
        metavar="output",
    )

    args=vars(parser.parse_args())
    get_data(**args)
