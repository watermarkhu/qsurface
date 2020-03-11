import pandas as pd
from progiter import ProgIter
import os

database = "eg_planar_3d_test"

def get_data(folder, output):


    print("reading data...")
    data = []

    onlyfiles = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]

    for file_path in ProgIter(onlyfiles):
        path = folder + file_path
        try:
            df = pd.read_csv(path, header=0)
            data.append(df.set_index(["L", "p"]))
        except:
            print("cound not read {}".format(path))

    cdata = data[0]

    print("processing data...")
    for i in ProgIter(range(1, len(data))):
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
        prog="csvCombiner",
        description="combines csv output files",
    )

    parser.add_argument("folder",
        action="store",
        type=str,
        help="directory of csv outputs",
        metavar="folder",
    )

    parser.add_argument("output",
        action="store",
        type=str,
        help="output, needs to add file ex.",
        metavar="output",
    )

    args=vars(parser.parse_args())
    get_data(**args)
