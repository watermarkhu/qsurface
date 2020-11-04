"""
The most popular decoder for surface codes is the Minimum-Weight Perfect Matching (MWPM) decoder. It performs near-optimal for a pauli noise model [dennis2002]_ on a standard toric code with a threshold of :math:`p_{\\text{th}} = 10.3\\%`, and for a phenomenological noise model (including faulty measurements) [wang2003]_, which includes faulty measurements, with :math:`p_{\\text{th}} = 2.9\\%`. The main idea is to approximate the error with the minimum-weight error configuration compatible with the syndrome. The minimum-weight configuration is found by constructing a fully connected graph between the nodes of the syndrome, which leads to a cubic worst-case time complexity [kolmogorov2009]_. 

The decoder defaults to using a Python implementation of MWPM by `networkx.algorithms.matching.max_weight_matching`. This implementation is however quite slow. Optionally, `Blossom V <https://pub.ist.ac.at/~vnk/software.html>`_ [kolmogorov2009]_, a C++ algorithm, can be used to increase the speed of the decoder. Since this software has its own license, it is not bundeled with OpenSurfaceSim. A script is provided to download and compile the latest release of BlossomV in `.get_blossomv`. The interface of the C++ code and Python is taken from `Fault Tolerant Simulations <https://github.com/naominickerson/fault_tolerance_simulations>`_.

"""

from . import sim
from . import plot
from shutil import copyfile as copy
import urllib.request
import tarfile
import os


blossom5_dir = "blossom5-v2.05.src"


def get_blossomv(accept: bool = False):
    """Downloads and compiles the BlossomV algorithm, which is distributed under the following license:
    
    License:

    .. include:: ../../../opensurfacesim/decoders/mwpm/blossom5/LICENSE
        :literal:
    """

    folder = os.path.dirname(os.path.abspath(__file__))

    try:
        with open(folder + "/blossom5/LICENSE", "r") as licensefile:
            lines = "_"*49
            print(f"The Blossom V algorithm is distributed under a different license:\n{lines}\n")
            print(licensefile.read(), end=f"{lines}\n")
    except FileNotFoundError:
        raise FileNotFoundError("License file missing. Automatic download is disabled.")

    if not accept:
        accept = input(
            "This function will download the software from https://pub.ist.ac.at/~vnk/software.html, do you wish to continue? [y/n]"
        )
        if accept not in ["y", "yes", "Y", "Yes", "YES"]:
            return

    url = "https://pub.ist.ac.at/~vnk/software/{}.tar.gz".format(blossom5_dir)
    file = urllib.request.urlopen(url)
    tar = tarfile.open(fileobj=file, mode="r:gz")
    tar.extractall(folder)
    tar.close()

    print(folder)
    os.rename(
        folder + f"/{blossom5_dir}/Makefile",
        folder + f"/{blossom5_dir}/defaultMakefile",
    )
    copy(folder + "/blossom5/Makefile", folder + f"/{blossom5_dir}/Makefile")
    copy(folder + "/blossom5/pyInterface.cpp", folder + f"/{blossom5_dir}/pyInterface.cpp")

    if os.system("make -v") == 0 and os.system("gcc -v") == 0:
        os.system(f"cd {folder}/{blossom5_dir} && make")
    else:
        print(
            "The required compilers (GCC & make) for Blossom 5 is not installed. \nPlease install and build in the blossom5 folder with the included Makefile. If this is not possible, please use the networkx version of the MWPM decoder."
        )
