
# Open Surface code Simulations

[![Unitary Fund](https://img.shields.io/badge/Supported%20By-UNITARY%20FUND-brightgreen.svg?style=for-the-badge)](http://unitary.fund)

This repository provides a simulation package for the surface code. The toric and planar lattices are currently supported. Each lattice is simulated by a *graph* of nodes and edges, where the *stars* and *plaquettes* are the nodes and qubits are the edges on the graph.

![alt text][toric4]

## Surface graphs

* `graph2D`, 2D graph
* `graph3D`, 3D(2+1D) graph

In the case of only Pauli errors, a 2D graph is generated for the simulation. If measurement errors are present, a 3D (2+1D) graph is generated instead.

## Decoders

* `mwpm`, Minimum Weight Perfect Matching
* `uf`, Union-Find
* `ufbb`, Union-Find Balanced Bloom

Several decoder algorithms are supported. The *Mininum-Weight Perfect Matching* (MWPM) decoder uses Kolmogorov's [Blossom V](https://pub.ist.ac.at/~vnk/software.html) algorithm. Furthermore, we implement Delfosse's and Nickerson's [Union-Find decoder](https://arxiv.org/pdf/1709.06218.pdf), which has *almost-linear* complexity. Finally, we present our modification to the Union-Find decoder; the **Balanced Bloom** algorithm, which improves the threshold of the Union-Find decoder to near MWPM performance, while retaining low complexity.

## Requirements
### MWPM decoder

The Blossom V algorithm is written in C, and can simply be compiled using the included makefile. The integration with the Python code is taken from [this repository](https://github.com/naominickerson/fault_tolerance_simulations) and provided by `PyMatch.py`. For more information we refer to the readme within the *blossom5* folder.

### Python packages

Though this repository, several non-standard python libraries are used, which includes:

**core packages**
* matplotlib
* scipy
* numpy
* pandas

**printing and info**
* progiter
* pprint
* git-python
* pyparsing
* termcolor

All required packages can be installed through:
```
pip install -r requirements.txt
```

## Usage simulation

### Command line
The file `run_oopsc.py` supports command line arguments. A simulation on a 3D planar 8x8x8 lattice with Pauli X and measurent error rate `px = pmx = 0.03` for 1000 iterations can be initiated with:
```
python run_oopsc.py 8 -l planar -px 0.03 -pmx 0.03 -i 1000
```
For more information on command line arguments type:
```
python run_oopsc.py --help
```

### built-in methods
In `oopsc.oopsc.py`, there are 3 methods to start a computation.
```python
output = single(size, dec, go, config, **kwargs)
output = multiple(size, dec, go, config, iters, **kwargs)
output = multiprocess(size, dec, go, config, iters, processes=None, **kwargs)
```

each accepting the following keyword arguments:
```python
kwargs = dict(
    ltype="toric",
    paulix=0,
    pauliz=0,
    erasure=0,
    measurex=0,
    measurez=0
  )
```
The `config` parameter is a dictionary containing decoder and plotting parameters and must be complete. It contains all long arguments listed by `python run_oopsc.py --help`. A complete config dictionary can be called by:
```python
config = oopsc.default_config()
```
The config can be changed by inputting keyworded arguments into the default config function:
```python
config = oopsc.default_config(plot3D=True, plot_bucket=True)
```

The `go` and `dec` parameters stand for *graph object* and *decoder*, respectively, which can be either of the items listed above. For the `multiprocess` method, one can specify the number of threads to use. If none is specified, the program will automatically choose to use all available threads.

## Plotting

Most of the config parameters are on the plotting of the lattice, which can be toggled on. There are 3 types of plots that can be toggled:
* 2D lattice plot (also final layer of 3D lattice)
![alt text][planar12]

* 3D lattice plot (see top)

* UF-graph plot
![alt text][uftoric6]


For all options, view the command line help:
```
python run_oopsc.py --help
```

## Usage thresholds

Threshold calculations can be done via `threshold_run.py`, e.g. a threshold calculation on a toric lattice with the MWPM decoder for p-error `[0.09, 0.1, 0.11]` and lattices `[8, 10, 12]` including measurement errors with each 1000 iterations:
```
python run_threshold.py mwpm toric 1000 -l 8 10 12 -p 0.09 0.1 0.11
```
for all options, view the command line help:
```
python run_threshold.py --help
```
The threshold values is stored in a csv file in the `\data` folder in the main directory, or in the directory indicated. One could recalculate the threshold using different fitting parameters using `threshold_fit.py` (see `python threshold_fit.py --help`) and replot the data with `threshold_plot.py` (see `python threshold_plot.py --help`)


## Issues

### Windows
Interactive plotting on windows might require installation of Python via the [Anaconda](https://www.anaconda.com/) or [Canopy](https://assets.enthought.com/downloads/) distributions that will work out of the box.

We have not been able to use the Blossom V algorithm on Windows due to compile errors. We do not recommend the installation of *Cygwin*, *GNU make* or similar executables as all have failed in our own experience. In stead, we encourage users to install the [Windows Subsystem for Linux (WSL)](https://docs.microsoft.com/en-us/windows/wsl/install-win10) on Windows.

After installation of WSL, one needs to do a few more steps in order to display plots and other GUI's.
1. Download a X-server such as [Xming](https://sourceforge.net/projects/xming/) or [VcsXrv](https://sourceforge.net/projects/vcxsrv/) (recommended).
2. Check your WSL version. Open a Powershell or CMD window and input `wsl -l -v`.
3. If your WSL version is 1, set `export DISPLAY=localhost:0.0` (add to `~/.bashrc` to make permanent). If you WSL is version 2, set `export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0` and add `-ac` to your X-server startup commands.
4. Make sure that your firewall is not blocking any connections to WSL. This can be done by the following PowerShell script `Set-NetFirewallProfile -Name public -DisabledInterfaceAliases "vEthernet (WSL)`. 

### Linux/WSL
Make sure to install tkinter via `sudo apt-get update` and `sudo apt-get install python3-tk`.
In case of any errors involvig the *backend* or *renderer* please uninstall via `pip uninstall matplotlib` and reinstall via the package manager. On Debian/Ubuntu this is done via `sudo apt-get install python-matplotlib`.



*This project is proudly funded by the [Unitary Fund](https://unitary.fund/).*

[uftoric6]: https://raw.githubusercontent.com/watermarkhu/oop_surface_code/master/images/uftoric3d_6.png "UF toric graph 6x6x6"
[planar12]: https://raw.githubusercontent.com/watermarkhu/oop_surface_code/master/images/planar2d_12.png "Planar lattice 12x12"
[toric4]: https://raw.githubusercontent.com/watermarkhu/oop_surface_code/master/images/toric3d_4.png "Toric lattice 4x4x4"
