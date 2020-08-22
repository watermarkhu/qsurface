
import matplotlib.pyplot as plt
import numpy as np

def latex_style(scale=0.9, y=None):
    fig_width_pt = 433.62
    inches_per_pt = 1.0/72.27                       # Convert pt to inch
    golden_mean = (np.sqrt(5.0)-1.0)/2.0

    fig_width = fig_width_pt*inches_per_pt*scale    # width in inches
    fig_height = fig_width*golden_mean if y is None else fig_width*y

    pgf_with_latex = {                      # setup matplotlib to use latex for output
        "pgf.texsystem": "pdflatex",        # change this if using xetex or lautex
        "text.usetex": True,                # use LaTeX to write all text
        "font.family": "serif",
        # blank entries should cause plots to inherit fonts from the document
        "font.serif": [],
        "font.sans-serif": [],
        "font.monospace": [],
        "axes.labelsize": 10,               # LaTeX default is 10pt font.
        "font.size": 10,
        "legend.fontsize": 8,               # Make the legend/label fonts a little smaller
        "xtick.labelsize": 8,
        "ytick.labelsize": 8,
        # default fig size of 0.9 textwidth
        "figure.figsize": [fig_width, fig_height],
        "pgf.preamble": [
            # use utf8 fonts becasue your computer can handle it :)
            r"\usepackage[utf8x]{inputenc}",
            # plots will be generated using this preamble
            r"\usepackage[T1]{fontenc}",
        ]
    }
    plt.rcParams.update(pgf_with_latex)


def plot_style(ax, title=None, xlabel=None, ylabel=None, gridstyle=":", gridwidth=0.5, **kwargs):
    ax.grid(linestyle=gridstyle, linewidth=gridwidth)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    for key, arg in kwargs.items():
        func = getattr(ax, f"set_{key}")
        func(arg)


def get_markers():
    return ["o", "s", "D", "p", "v", "<", "^", ">", "*", "P", "X", "h", "H", "d", 4, 5, 6, 7, 8, 9, 10, 11]


def get_colors():
    return {
        "SUF":    "C4",
        "DUF":    "C1",
        "SBUF":   "C2",
        "DBUF":   "C3",
        "MWPM":   "C0",
        "UFBB":   "C8",
    }


def get_linestyles():
    return {
        "SUF":    "--",
        "DUF":     ":",
        "SBUF":     "-.",
        "DBUF":      (0, (5, 1)),
        "MWPM":         "-",
        "UFBB":        (0, (3, 1, 1, 1, 1, 1)),
    }


def legend_style():
    return dict(markerscale=1, fontsize="small", columnspacing=0, labelspacing=0.2, handletextpad=0, numpoints=1)
