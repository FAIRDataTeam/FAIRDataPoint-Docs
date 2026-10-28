# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/config

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))


# -- Project information -----------------------------------------------------

project = 'FAIR Data Point'
copyright = '2026, FAIR Data Team'
author = 'FAIR Data Team'

# The FAIRDataPoint (back-end) version described by these docs.
# The full version, including alpha/beta/rc tags
release = '1.22.2'
version = '1.22'

# Docker image versions used in the examples.
# Keep these in line with the defaults in the FAIRDataTeam/compose submodule
# (docs/deployment/compose/fdp/components).
fdp_version = release
fdp_client_version = '1.18.1'
mongo_version = '8.2.12'
graphdb_version = '10.8.14'

rst_prolog = f"""

.. |fdp_ver| replace:: {fdp_version}
.. |fdp_client_ver| replace:: {fdp_client_version}
.. |mongo_ver| replace:: {mongo_version}
.. |graphdb_ver| replace:: {graphdb_version}

"""


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx_substitution_extensions',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = []

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# Example hosts and local URLs used in the documentation are not checked by `sphinx-build -b linkcheck`.
linkcheck_ignore = [
    r'https?://localhost.*',
    r'https?://([a-z0-9-]+\.)*example\.(com|org).*',
    r'https://w3id\.org/example/.*',
]


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

html_favicon = '_static/favicon.ico'
html_theme_options = {
    'version_selector': True,
}

def setup(app):
    app.add_css_file('style.css')

    make_confval(app)


def make_confval(app):
    # Copy-pasted from https://github.com/rtfd/sphinx_rtd_theme
    from sphinx.locale import _
    from sphinx.domains.python import PyField
    from sphinx.util.docfields import Field

    app.add_object_type(
        'confval',
        'confval',
        objname='configuration value',
        indextemplate='pair: %s; configuration value',
        doc_field_types=[
            PyField(
                'type',
                label=_('Type'),
                has_arg=False,
                names=('type',),
                bodyrolename='class'
            ),
            Field(
                'default',
                label=_('Default'),
                has_arg=False,
                names=('default',),
            ),
        ]
    )
