# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.

import os
import sys

sys.path.insert(0, os.path.abspath("../../"))
import sphinx
from m2r2 import MdInclude

# -- Project information -----------------------------------------------------

project = "Open Surface code Simulations"
copyright = "2020, Mark Shui Hu"
author = "Mark Shui Hu"


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.napoleon",
    "sphinx.ext.autodoc",
    "sphinx_autodoc_typehints",
    "sphinx.ext.todo",
    "sphinx.ext.githubpages",
    "sphinx.ext.intersphinx",
    "m2r2",
    "sphinx_rtd_theme",
]

intersphinx_mapping = {"matplotlib": ("https://matplotlib.org/", None)}
intersphinx_mapping = {"networkx": ("https://networkx.github.io/documentation/stable/", None)}


# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation f~or
# a list of builtin themes.
#
# html_theme = 'alabaster'
# html_theme_options = {
#     'description': 'Open source library for simulating and visualizing the surface code and its decoders.',
#     'github_user': 'watermarkhu',
#     'github_repo': 'OpenSurfaceSim',
#     'github_button': True,
#     'codecov_button': True,
#     "extra_nav_links": {"Contact author": "https://watermarkhu.nl"},
#     "sidebar_collapse": False,
#     "show_powered_by": False,
#     # 'font_family': '"Charis SIL", "Noto Serif", serif',
#     # 'head_font_family': 'Lato, sans-serif',
#     # 'code_font_family': '"Code new roman", "Ubuntu Mono", monospace',
#     # 'code_font_size': '1rem',
# }

html_theme = "sphinx_rtd_theme"
html_theme_options = {
    "analytics_id": "UA-180556212-1",
    "includehidden": True,
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = []
# html_sidebars = {
#     '**': [
#         'globaltoc.html',
#         'localtoc.html',
#         'relations.html',
#         'sourcelink.html',
#         'searchbox.html',
#         # located at _templates/
#         #  'foo.html',
#     ]

# }

# -- Extension configuration -------------------------------------------------

# m2r_parse_relative_links = True
# m2r_anonymous_references = False
# m2r_disable_inline_math = False

# -- Options for todo extension ----------------------------------------------

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True

default_role = "obj"
