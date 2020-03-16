'''
2020 Mark Shui Hu, QuTech

www.github.com/watermarkhu/oop_surface_code
_____________________________________________
'''

import matplotlib.pyplot as plt
from threshold_fit import read_data
from matplotlib.lines import Line2D
from threshold_plot import plot_style


def plot_compare(csv_names, xaxis, probs, latts, feature, plot_error, dim, xm, output, **kwargs):

    xchoice = dict(p="p", P="p", l="L", L="L")
    ychoice = dict(p="L", P="L", l="p", L="p")
    xchoice, ychoice = xchoice[xaxis], ychoice[xaxis]
    xlabels, ylabels = (probs, latts) if xaxis == "p" else (latts, probs)
    if xlabels: xlabels = sorted(xlabels)

    linestyles = ['-', '--', ':', '-.']

    data, leg = [], []
    for i, name in enumerate(csv_names):
        ls = linestyles[i%len(linestyles)]
        leg.append(Line2D([0], [0], ls=ls, label=name))
        data.append(read_data(name))

    if not ylabels:
        ylabels = set()
        for df in data:
            for item in df.index.get_level_values(ychoice):
                ylabels.add(round(item, 6))
        ylabels = sorted(list(ylabels))


    colors = {ind: f"C{i}" for i, ind in enumerate(ylabels)}

    xset = set()
    for i, df in enumerate(data):

        ls = linestyles[i%len(linestyles)]

        for ylabel in ylabels:

            color = colors[ylabel]

            d = df.loc[df.index.get_level_values(ychoice) == ylabel]
            index = [round(v, 6) for v in d.index.get_level_values(xchoice)]
            d = d.reset_index(drop=True)
            d["index"] = index
            d = d.set_index("index")


            if not xlabels:
                X = index
                xset = xset.union(set(X))
            else:
                X = [x for x in xlabels if x in d.index.values]

            column = feature if feature in df else f"{feature}_m"
            Y = [d.loc[x, column] for x in X]

            if dim != 1:
                X = [x**dim for x in X]

            if i == 0:
                plt.plot(X, Y, ls=ls, c=color, label=f"{ychoice}={ylabel}")
            else:
                plt.plot(X, Y, ls=ls, c=color)

            if plot_error and f"{feature}_v" in d:
                E = list(d.loc[:, f"{feature}_v"])
                ym = [y - e for y, e in zip(Y, E)]
                yp = [y + e for y, e in zip(Y, E)]
                plt.fill_between(X, ym, yp, alpha=0.1, facecolor=color, edgecolor=color, ls=ls, lw=2)


    xnames = sorted(list(xset)) if not xlabels else xlabels
    xticks = [x**dim for x in xnames]
    xnames = [round(x*xm, 3) for x in xnames]

    plt.xticks(xticks, xnames)
    leg1 = plt.legend(handles=leg, loc="lower right")
    plt.legend(ncol=3)
    plt.gca().add_artist(leg1)
    plot_style(plt.gca(), "heuristic of {}".format(feature), xchoice, "{} count".format(feature))
    plt.show()



if __name__ == "__main__":

    import argparse
    from oopsc import add_kwargs

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

    parser.add_argument("xaxis",
        action="store",
        type=str,
        help="xaxis of comparison {l/p}",
        choices=["l", "p"],
        metavar="xaxis")

    key_arguments= [
        ["-n", "--csv_names", "store", "CSV databases to plot - verbose list str", dict(type=str, nargs='*', metavar="", required=True)],
        ["-p", "--probs", "store", "p items to plot - verbose list", dict(type=float, nargs='*', metavar="")],
        ["-l", "--latts", "store", "L items to plot - verbose list", dict(type=float, nargs='*', metavar="")],
        ["-e", "--plot_error", "store_true", "plot standard deviation - toggle", dict()],
        ["-a", "--average", "store_true", "average p - toggle", dict()],
        ["-d", "--dim", "store", "dimension", dict(type=int, default=1, metavar="")],
        ["-m", "--xm", "store", "x axis multiplier", dict(type=int, default=1, metavar="")],
        ["-o", "--output", "store", "output file name", dict(type=str, default="", metavar="")],
    ]
    add_kwargs(parser, key_arguments)
    args=vars(parser.parse_args())

    plot_compare(**args)
