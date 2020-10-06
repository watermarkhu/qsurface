from shutil import copyfile as copy
import urllib.request
import tarfile
import os


blossom5_dir = "blossom5-v2.05.src"


def run():

    folder = os.path.dirname(os.path.abspath(__file__))

    try:
        with open(folder + "/blossom5/LICENSE", "r") as licensefile:
            print(licensefile.read())
    except FileNotFoundError:
        raise FileNotFoundError("License file missing. Automatic download is disabled.")

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

if __name__ == "__main__":
    run()