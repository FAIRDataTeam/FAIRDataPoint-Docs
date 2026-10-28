***********************
Contribution guidelines
***********************

The FAIR Data Point repositories are open source and you can contribute via GitHub:

- https://github.com/FAIRDataTeam/FAIRDataPoint
- https://github.com/FAIRDataTeam/FAIRDataPoint-client
- https://github.com/FAIRDataTeam/FAIRDataPoint-Docs
- https://github.com/FAIRDataTeam/compose (Docker compose files used for development, testing, and the examples in this documentation)
- https://github.com/FAIRDataTeam/FAIRDataPoint-UI (the new user interface, under development)

To contribute, fork the relevant repository, create a new branch, make your changes, and `open a pull request <https://docs.github.com/en/pull-requests/how-tos/create-pull-requests/creating-a-pull-request-from-a-fork>`_.

Developers with write access don't need to fork, but they do need to use a branch and pull-request workflow.

All changes must be made via pull requests in order to facilitate consistent auto-generated changelogs via `GitHub releases <https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository>`_.

Documentation
=============

This documentation is written in `reStructuredText <https://docutils.sourceforge.io/rst.html>`_ and built with `Sphinx <https://www.sphinx-doc.org>`_.
The compose examples are included from the `FAIRDataTeam/compose <https://github.com/FAIRDataTeam/compose>`_ repository, which is a git submodule in ``docs/deployment/compose``.
To build the documentation locally:

.. code-block:: bash

    git clone --recurse-submodules https://github.com/FAIRDataTeam/FAIRDataPoint-Docs.git
    cd FAIRDataPoint-Docs
    pip install -r requirements.txt
    sphinx-build -M html ./docs ./docs/_build

When a new FDP or client version is released, update the version numbers in ``docs/conf.py`` and the compose submodule.
