import pandas as pd
from threshold_runsql import connect_database
from progiter import ProgIter



def get_data(database, tables):
    con = connect_database(database)

    print("reading data...")
    data = []
    for i in ProgIter(range(tables)):
        data.append(pd.read_sql_table("t_{}".format(i), con).drop(["id"], axis=1).set_index(["L", "p"]))

    cdata = data[0]

    print("processing data...")
    for i in ProgIter(range(1, tables)):
        pdata = data[i]

        for j in range(len(pdata)):
            prow = pdata.iloc[j,:]
            if prow.name not in cdata.index:
                cdata.append(prow)
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
    cdata.to_csv("./data/cartesius_{}.csv".format(database))


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

    parser.add_argument("tables",
        action="store",
        type=int,
        help="number of tables",
        metavar="tables",
    )

    args=vars(parser.parse_args())
    get_data(**args)
