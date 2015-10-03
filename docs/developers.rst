==========
Developers
==========

Grab the source from Github: https://github.com/kumar303/hawkrest

Run the tests
=============

You can run the full test suite with the `tox`_ command::

    tox

To just run Python 2.7 unit tests type::

    tox -e py27-django1.8-drf3.2

To just run doctests type::

    tox -e docs

Set up an environment
=====================

Using a `virtualenv`_ you can set yourself up for development like this::

    pip install -r requirements/dev.txt
    python setup.py develop

Note that this won't install any libraries that are tested at different
versions. You need tox for that.

Build the docs
==============

In your development virtualenv, you can build the docs like this::

    make -C docs/ html doctest
    open docs/_build/html/index.html

Publish a release
=================

To publish a new release on `PyPI`_, make sure the changelog is up to date
and make sure you bumped the module version in ``setup.py``. Tag master
at the version. For example, something like::

    git tag 0.0.5
    git push --tags

Run this from the repository root to publish on `PyPI`_::

    python setup.py sdist register upload


.. _virtualenv: https://pypi.python.org/pypi/virtualenv
.. _tox: http://tox.readthedocs.org/
.. _`PyPI`: https://pypi.python.org/pypi
