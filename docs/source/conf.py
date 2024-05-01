import os
import sys
import django
django_version = django.get_version()
sys.path.insert(0, os.path.abspath('../../'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'webapps2024.settings'
django.setup()

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'FakePal - An Online Payment System'
copyright = '2024, Tom Naccarato'
author = 'Tom Naccarato'
python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['sphinx.ext.autodoc']

templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

rst_epilog = f"""
.. |python_version| replace:: {python_version}
.. |django_version| replace:: {django_version}
"""
