'''
2020 Mark Shui Hu, QuTech

www.github.com/watermarkhu/oop_surface_code
_____________________________________________
'''

import matplotlib.pyplot as plt
from threshold_fit import read_data
from matplotlib.lines import Line2D
from threshold_plot import plot_style


def plot_compare(folder, csv_names, feature, plot_error, lattices):

    linestyles = ['-', '--', ':', '-.']

    leg = []
    colors = {}
    for i, name in enumerate(csv_names):

        ls = linestyles[i%len(linestyles)]
        leg.append(Line2D([0], [0], ls=ls, label=name))

        file_path = folder + name + ".csv"
        data = read_data(file_path, lattices)

        for j, L in enumerate(sorted(list(set(data.index.get_level_values("L"))))):

            if L in colors:
                color = colors[L]
            else:
                color = colors[L] = "C{}".format(j)

            df = data.iloc[data.index.get_level_values('L') == L]
            P = [p*100 for p in list(df.index.get_level_values("p"))]

            if feature in df:
                Y = list(df.loc[:, feature])
            else:
                Y = list(df.loc[:, f"{feature}_m"])

            if i == 0:
                plt.plot(P, Y, ls=ls, c=color, label=f"L={L}")
            else:
                plt.plot(P, Y, ls=ls, c=color)

            if plot_error:
                E = list(df.loc[:, f"{feature}_v"])
                ym = [y - e for y, e in zip(Y, E)]
                yp = [y + e for y, e in zip(Y, E)]
                plt.fill_between(P, ym, yp, alpha=0.1, facecolor=color, edgecolor=color, ls=ls, lw=2)


    leg1 = plt.legend(handles=leg, loc="lower right")
    plt.legend()
    plt.gca().add_artist(leg1)
    plot_style(plt.gca(),"heuristic of {}".format(feature), "pX", "{} count".format(feature))
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
        ["-l", "--lattices", "store", "lattice sizes - verbose list int", dict(type=int, nargs='*', metavar="")],
        ["-e", "--plot_error", "store_true", "plot standard deviation - toggle", dict()],
        ["-f", "--folder", "store", "base folder path - toggle", dict(default="./data/", metavar="")],
    ]
    add_args(parser, key_arguments)

    args=vars(parser.parse_args())
    plot_compare(**args)
