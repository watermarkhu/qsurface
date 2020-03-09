'''
2020 Mark Shui Hu, QuTech

www.github.com/watermarkhu/oop_surface_code
_____________________________________________
'''

import matplotlib.pyplot as plt
from threshold_fit import read_data
from matplotlib.lines import Line2D
from collections import defaultdict as dd
from threshold_plot import plot_style


def plot_compare(folder, csv_names, feature, plot_error, probs, dim, average):

    linestyles = ['-', '--', ':', '-.']

    leg = []
    colors = {}
    Lset = set()
    avg = dd(list)
    for i, name in enumerate(csv_names):

        ls = linestyles[i%len(linestyles)]
        leg.append(Line2D([0], [0], ls=ls, label=name))

        file_path = folder + name + ".csv"
        data = read_data(file_path)

        if probs is None:
            probs = sorted([round(p, 6) for p in list(set(data.index.get_level_values("p")))])

        for j, p in enumerate(probs):

            if p in colors:
                color = colors[p]
            else:
                color = colors[p] = "C{}".format(j)

            df = data.iloc[data.index.get_level_values('p') == p]
            L = [l**dim for l in list(df.index.get_level_values("L"))]

            for l in list(df.index.get_level_values("L")):
                Lset.add(l)

            if feature in df:
                Y = list(df.loc[:, feature])
            else:
                Y = list(df.loc[:, f"{feature}_m"])

            if not average:

                if i == 0:
                    plt.plot(L, Y, ls=ls, c=color, label=f"p={p}")
                else:
                    plt.plot(L, Y, ls=ls, c=color)

                if plot_error:
                    E = list(df.loc[:, f"{feature}_v"])
                    ym = [y - e for y, e in zip(Y, E)]
                    yp = [y + e for y, e in zip(Y, E)]
                    plt.fill_between(L, ym, yp, alpha=0.1, facecolor=color, edgecolor=color, ls=ls, lw=2)

            else:

                for l, y in zip(L, Y):
                    avg[l].append(y)

        if average:

            L = sorted(list(avg.keys()))
            Y = []
            for l in L:
                Y.append(sum(avg[l])/len(avg[l]))

            plt.plot(L, Y, ls=ls, c=color)



    Llabels = sorted(list(Lset))
    Lticks = [l ** dim for l in Llabels]

    plt.xticks(Lticks, Llabels)
    leg1 = plt.legend(handles=leg, loc="lower right")
    plt.legend(ncol=3)
    plt.gca().add_artist(leg1)

    plot_style(plt.gca(), "heuristic of {}".format(feature), "L", "{} count".format(feature))

    plt.show()



if __name__ == "__main__":

    import argparse
    from oopsc import add_args

    parser = argparse.ArgumentParser(
        prog="mysql creator",
        description="creates a mysql database",
    )

    parser.add_argument("feature",
        action="store",
        type=str,
        help="feature to plot",
        metavar="feat",
    )

    key_arguments= [
        ["-n", "--csv_names", "store", "CSV databases to plot - verbose list str", dict(type=str, nargs='*', metavar="", required=True)],
        ["-p", "--probs", "store", "probabilities - verbose list int", dict(type=float, nargs='*', metavar="")],
        ["-e", "--plot_error", "store_true", "plot standard deviation - toggle", dict()],
        ["-a", "--average", "store_true", "average p - toggle", dict()],
        ["-f", "--folder", "store", "base folder path - toggle", dict(default="./data/", metavar="")],
        ["-d", "--dim", "store", "dimension - toggle", dict(type=int, default=1, metavar="")],

    ]
    add_args(parser, key_arguments)

    args=vars(parser.parse_args())
    plot_compare(**args)
