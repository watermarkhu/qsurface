from setuptools import setup, find_packages
import pathlib


directory = pathlib.Path(__file__).parent

README = (directory / "README.md").read_text()


setup(
    name="qsurface",
    version="0.1.3",
    description="Open library from surface code simulations and visualizations",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/watermarkhu/qsurface",
    project_urls={"Documentation": "https://qsurface.readthedocs.io/en/latest/"},
    author="Mark Shui Hu",
    author_email="watermarkhu@gmail.com",
    license="BSD-3",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3.7",
        "Topic :: Scientific/Engineering :: Physics",
    ],
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*"]),
    include_package_data=True,
    python_requires=">3.7.0",
    install_requires=[
        "matplotlib>=3.3.2",
        "networkx>=2.0",
        "pandas>=1.1.0",
        "scipy>=1.4.0",
        "pptree>=3.1",
    ],
    entry_points={
        "console_scrips": [
            "qsurface=qsurface.__main__:main",
            "qsurface-getblossomv=qsurface.decoders.mwpm:get_blossomv",
        ],
    },
)
