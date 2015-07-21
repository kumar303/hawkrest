==========
Developers
==========

Grab the source from Github: https://github.com/kumar303/hawkrest

Run the tests
=============

You can run the full test suite with the `tox`_ command::

    tox

To just run Python 2.7 unit tests type::

    tox -e py27

To just run doctests type::

    tox -e docs

Set up an environment
=====================

Using a `virtualenv`_ you can set yourself up for development like this::

    pip install -r requirements/dev.txt
    python setup.py develop

Build the docs
==============

In your development virtualenv, you can build the docs manually like this::

    make -C docs/ html doctest
    open docs/_build/html/index.html

Publish a release
=================

To publish a new release on `PyPI`_, make sure the changelog is up to date
and make sure you bumped the module version in ``setup.py``. Run this
from the repository root::

    python setup.py sdist register upload


.. _virtualenv: https://pypi.python.org/pypi/virtualenv
.. _tox: http://tox.readthedocs.org/
.. _`PyPI`: https://pypi.python.org/pypi
