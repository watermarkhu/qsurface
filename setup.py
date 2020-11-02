from setuptools import setup, find_packages
import pathlib


directory = pathlib.Path(__file__).parent

README = (directory / "README.md").read_text()


setup(
    name="opensurfacesim",
    version="0.1.0",
    description="Open library from surface code simulations and visualizations",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/watermarkhu/opensurfacesim",
    author="Mark Shui Hu",
    author_email="watermarkhu@gmail.com",
    license="BSD-3",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3.7",
        "Topic :: Scientific/Engineering :: Physics",
    ],
    packages=find_packages(exclude=['tests', '*.tests', '*.tests.*']),
    include_package_data = True,
    install_requires=[
        "matplotlib",
        "networkx",
        "pandas",
        "scipy",
        "pptree",
    ],
    entry_points={
        "console_scrips":[
            "py-opensurfacesim=opensurfacesim.__main__:main",
            "opensurfacesim-getblossomv=opensurfacesim.decoders.mwpm:get_blossomv",
        ],
    },
)
