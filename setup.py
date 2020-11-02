from setuptools import setup

setup(name='opensurfacesim',
      version=0.1,
      description="Open library from surface code simulations and visualizations",
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3.7',
        'Topic :: Scientific/Engineering :: Physics',
      ],
      url="https://github.com/watermarkhu/opensurfacesim",
      author="Mark Shui Hu",
      author_email="watermarkhu@gmail.com",
      license="BSD-3",
      packages=["opensurfacesim"],
      install_requires=[
            "matplotlib",
            "networkx",
            "pandas",
            "scipy",
            "pptree",
      ]
      zip_safe=False,
      entry_points = {
            "console_scrips": ["opensurfacesim-getblossomv=opensurfacesim.decoders.mwpm:get_blossomv"],
      }
)

