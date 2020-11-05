
# opensurfacesim

![Build](https://github.com/watermarkhu/opensurfacesim/workflows/Build/badge.svg)
[![codecov](https://codecov.io/gh/watermarkhu/OpenSurfaceSim/branch/master/graph/badge.svg?token=CWLVPDFF2L)](https://codecov.io/gh/watermarkhu/OpenSurfaceSim)
[![Documentation Status](https://readthedocs.org/projects/opensurfacesim/badge/?version=latest)](https://opensurfacesim.readthedocs.io/en/latest/?badge=latest)
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/watermarkhu/opensurfacesim/master?filepath=examples.ipynb)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.4247617.svg)](https://doi.org/10.5281/zenodo.4247617)
[![Unitary Fund](https://img.shields.io/badge/Supported%20By-UNITARY%20FUND-brightgreen.svg?style=flat-the-badge)](http://unitary.fund)

Opensurfacesim is a simulation package for the surface code, and is designed to modularize 3 aspects of a surface code simulation.

1. The surface code
2. The error model
3. The used decoder

New types of surface codes, error modules and decoders can be added to opensurfacesim by using the included templates for each of the three core module categories.

The current included decoders are:

* The *Mininum-Weight Perfect Matching* (`mwpm`) decoder.
* [Delfosse's and Nickerson's](https://arxiv.org/pdf/1709.06218.pdf) *Union-Find* (`unionfind`) decoder, which has *almost-linear* worst-case time complexity.
* Our modification to the Union-Find decoder; the *Union-Find Node-Suspension* (`ufns`) decoder, which improves the threshold of the Union-Find decoder to near MWPM performance, while retaining quasi-linear worst-case time complexity.

The compatibility of these decoders with the included surface codes are listed below.

| Decoders  | `toric` code | `planar` code |
|-----------|--------------|---------------|
|`mwpm`     |✅            |✅             |
|`unionfind`|✅            |✅             |
|`ufns`     |✅            |✅             |

# Installation

All required packages can be installed through:

```bash
pip install opensurfacesim
```

## Requirements

* Python 3.7+
* Tkinter for interactive plotting. Your Python distribution may or may not bundled Tkinter already. Check out this [guide](https://realpython.com/python-gui-tkinter/)  from realpython.com to install Tkinter if you encounter any problems.
* Matplotlib 3.4+ for plotting on a 3D lattice (Refers to a future release of matplotlib, see [pull request](https://github.com/matplotlib/matplotlib/pull/18816))

### MWPM decoder

The MWPM decoder utilizes `networkx` for finding the minimal weights in a fully connected graph. This implementation is however rather slow compared to Kolmogorov's [Blossom V](https://pub.ist.ac.at/~vnk/software.html) algorithm. Blossom V has its own license and is thus not included with opensurfacesim. We do provided a single function to download and compile Blossom V, and to setup the integration with opensurfacesim automatically.

```python
>>> from opensurfacesim.decoders import mwpm
>>> mwpm.get_blossomv()
```

# Usage

To simulate the toric code and simulate with bitflip error for 10 iterations and decode with the MWPM decoder:

```python
>>> from opensurfacesim.main import initialize, run
>>> code, decoder = initialize((6,6), "toric", "mwpm", enabled_errors=["pauli"])
>>> run(code, decoder, iterations=10, error_rates = {"p_bitflip": 0.1})
{'no_error': 8}
```

Benchmarking of decoders can be enabled by attaching a *benchmarker* object to the decoder. See the docs for the syntax and information to setup benchmarking.

```python
>>> from opensurfacesim.main import initialize, run
>>> benchmarker = BenchmarkDecoder({"decode":"duration"})
>>> run(code, decoder, iterations=10, error_rates = {"p_bitflip": 0.1}, benchmark=benchmarker)
{'no_error': 8,
'benchmark': {'success_rate': [10, 10],
'seed': 12447.413636559,
'durations': {'decode': {'mean': 0.00244155000000319,
'std': 0.002170364089572033}}}}
```

The figures in opensurfacesim allows for step-by-step visualization of the surface code simulation (and if supported the decoding process). Each figure logs its history such that the user can move backwards in time to view past states of the surface (and decoder). Press `h` when the figure is open for more information.

```python
>>> from opensurfacesim.main import initialize, run
>>> code, decoder = initialize((6,6), "toric", "mwpm", enabled_errors=["pauli"], plotting=True, initial_states=(0,0))
>>> run(code, decoder, error_rates = {"p_bitflip": 0.1, "p_phaseflip": 0.1}, decode_initial=False)
```

![Interactive plotting on a 6x6 toric code.](https://raw.githubusercontent.com/watermarkhu/OpenSurfaceSim/master/images/toric-2d.gif "Iteractive plotting on a 2d axis")

Plotting will be performed on a 3D axis if faulty measurements are enabled.

```python
>>> code, decoder = initialize((3,3), "toric", "mwpm", enabled_errors=["pauli"], faulty_measurements=True, plotting=True, initial_states=(0,0))
>>> run(code, decoder, error_rates = {"p_bitflip": 0.05, "p_bitflip_plaq": 0.05}, decode_initial=False)
```

![Interactive plotting on a toric code with faulty measurements.](https://raw.githubusercontent.com/watermarkhu/OpenSurfaceSim/master/images/toric-3d.gif "Iteractive plotting on a 3d axis")

Simulations can also be initiated from the command line

```bash
$ python -m opensurfacesim -e pauli -D mwpm -C toric simulation --p_bitflip 0.1 -n 10
{'no_error': 8}
```

For more information on command line interface:

```bash
$ python -m opensurfacesim -h
usage: opensurfacesim
...
```

*This project is proudly funded by the [Unitary Fund](https://unitary.fund/).*
