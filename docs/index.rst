.. Hawkrest documentation master file, created by
   sphinx-quickstart on Thu Feb 27 11:05:46 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

========
Hawkrest
========

`Hawk`_ HTTP Authorization for `Django Rest Framework`_.

Hawk lets two parties securely communicate with each other using
messages signed by a shared key.
It is based on `HTTP MAC access authentication`_ (which
was based on parts of `OAuth 1.0`_).

Hawkrest uses the `mohawk`_ module to add Hawk
authorization to your REST API views.

This guide will help you set everything up but you should
also read through `mohawk security considerations`_ to get familiar
with the security aspects of Hawk.


.. _`Hawk`: https://github.com/hueniverse/hawk
.. _`HTTP MAC access authentication`: http://tools.ietf.org/html/draft-hammer-oauth-v2-mac-token-05
.. _`Django Rest Framework`: http://django-rest-framework.org/
.. _`mohawk`: http://mohawk.readthedocs.org/
.. _`OAuth 1.0`: http://tools.ietf.org/html/rfc5849
.. _`mohawk security considerations`: http://mohawk.readthedocs.org/en/latest/security.html

.. _install:

Installation
============

Using `pip`_, install the module like this::

    pip install hawkrest

This will also install all necessary dependencies.
You'll most likely put this in a `requirements`_ file within your Django app.

The source code is available at https://github.com/kumar303/hawkrest

.. _`pip`: http://www.pip-installer.org/
.. _`requirements`: http://www.pip-installer.org/en/latest/user_guide.html#requirements-files

Topics
======

.. toctree::
   :maxdepth: 3

   usage
   developers

Bugs
====

You can report issues at https://github.com/kumar303/hawkrest

Changelog
=========

- **0.0.1** (unreleased)

  - Initial release, extracted from https://github.com/mozilla/apk-signer


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
