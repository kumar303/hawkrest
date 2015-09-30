.. HawkREST documentation master file, created by
   sphinx-quickstart on Thu Feb 27 11:05:46 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

========
HawkREST
========

`Hawk`_ HTTP Authorization for `Django Rest Framework`_.

.. image:: https://travis-ci.org/kumar303/hawkrest.png?branch=master
    :target: https://travis-ci.org/kumar303/hawkrest

Hawk lets two parties securely communicate with each other using
messages signed by a shared key.
It is based on `HTTP MAC access authentication`_ (which
was based on parts of `OAuth 1.0`_).

HawkREST uses the `mohawk`_ module to add Hawk
authorization to your REST API views.

This guide will help you set everything up but you should
also read through `mohawk security considerations`_ to get familiar
with the security aspects of Hawk.


.. _`Hawk`: https://github.com/hueniverse/hawk
.. _`HTTP MAC access authentication`: http://tools.ietf.org/html/draft-hammer-oauth-v2-mac-token-05
.. _`OAuth 1.0`: http://tools.ietf.org/html/rfc5849
.. _`mohawk security considerations`: http://mohawk.readthedocs.org/en/latest/security.html

.. _install:

Installation
============

Requirements:

* Python 2.7+ or 3.3+
* `Django Rest Framework`_
* `mohawk`_

Using `pip`_, install the module like this::

    pip install hawkrest

This will also install all necessary dependencies.
You'll most likely put this in a `requirements`_ file within your Django app.

The source code is available at https://github.com/kumar303/hawkrest

.. _`Django Rest Framework`: http://django-rest-framework.org/
.. _`mohawk`: http://mohawk.readthedocs.org/
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

- **0.0.6** (2015-09-08)

  - **IMPORTANT**: If migrating to this version from an earlier version of
    ``hawkrest``, your Django Rest Framework API views *must* require an
    authenticated user :ref:`as documented <protecting-api-views>`. In other
    words, older versions of ``hawkrest`` would reject any request that didn't
    have a Hawk authentication header but this version does not (see the bug fix
    below).
  - Fixed bug where other HTTP authorization schemes could not be supported at
    the same time as Hawk. Thanks to
    `Mauro Doglio <https://github.com/maurodoglio>`_ for the patch.
  - Fixed incorrect statement in docs that Python 2.6 was supported. Only 2.7 or
    greater is supported at this time.
  - Sends ``WWW-Authenticate: Hawk`` header in 401 responses now.

- **0.0.5** (2015-07-21)

  - Added `HAWK_CREDENTIALS_LOOKUP` setting which is a :ref:`callable <usage>`.
    Thanks to `Felipe Otamendi <https://github.com/felipeota>`_ for the patch.

- **0.0.4** (2015-06-24)

  - Fixed nonce callback support for
    `mohawk 0.3.0 <http://mohawk.readthedocs.org/en/latest/#changelog>`_.
    Thanks to Josh Wilson for the patches.

- **0.0.3** (2015-01-05)

  - Fixed traceback when cache setting is undefined.
    Thanks to wolfgangmeyers for the patch.

- **0.0.2** (2014-03-03)

  - Added support for Python 3.3 and greater
  - Added support for Python 2.6

- **0.0.1** (2014-02-27)

  - Initial release, extracted from https://github.com/mozilla/apk-signer

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
