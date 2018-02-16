.. _usage:

=====
Usage
=====

Django Configuration
====================

After :ref:`installation <install>`,
you'll need to configure your Django app with some
variables in your ``settings.py`` file.

Make sure the module is installed as an app:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'hawkrest',
    )

Make sure the middleware is installed by adding it to your project's
``MIDDLEWARE`` or ``MIDDLEWARE_CLASSES`` (Django version < 1.11) setting:

.. code-block:: python

    MIDDLEWARE = (
        ...
        'hawkrest.middleware.HawkResponseMiddleware',
    )

To protect all your REST views with Hawk, you can make hawkrest the
default:

.. code-block:: python

    REST_FRAMEWORK = {
        'DEFAULT_AUTHENTICATION_CLASSES': (
            'hawkrest.HawkAuthentication',
        ),
        ...
    }

Set up the allowed access credentials. Each dict key will be a Hawk ID for
a user who is
allowed to connect to your API. For example, an incoming request with an
ID named ``script-user`` would sign its request using the secret
``this should be a long secret string`` to make a successful connection.
The credentials dict in your settings file would look like this:

.. code-block:: python

    HAWK_CREDENTIALS = {
        'script-user': {
            'id': 'script-user',
            'key': 'this should be a long secret string',
            'algorithm': 'sha256'
        },
    }

You can add each Hawk credential to this dict.

If you need an alternative method for looking up credentials you can set up a
lookup function under the ``HAWK_CREDENTIALS_LOOKUP`` setting. This function
receives a Hawk ID as a parameter and returns a dict containing the
credentials. For example, if you have a ``HawkUser`` model with a ``key``
attribute then you can write a function ``hawk_credentials_lookup`` as follows:

.. code-block:: python

    def hawk_credentials_lookup(id):
        user = HawkUser.objects.get(some_id=id)
        return {
            'id': id,
            'key': user.key,
            'algorithm': 'sha256'
        }

and then you would configure it in your settings:

.. code-block:: python

    HAWK_CREDENTIALS_LOOKUP = 'yourapi.auth.hawk_credentials_lookup'

Alternately, you can subclass ``HawkAuthentication`` and override the ``hawk_credentials_lookup()`` method. For example:

.. code-block:: python

    from hawkrest import HawkAuthentication

    class YourHawk(HawkAuthentication):
        def hawk_credentials_lookup(self, id):
            user = HawkUser.objects.get(some_id=id)
            return {
                'id': id,
                'key': user.key,
                'algorithm': 'sha256'
            }

and then specify your new class instead in the authentication backend list:

.. code-block:: python

    REST_FRAMEWORK = {
        'DEFAULT_AUTHENTICATION_CLASSES': (
            'yourapi.auth.YourHawk',
        ),
        ...
    }

By default, a generic ``HawkAuthenticatedUser`` instance is returned when valid Hawk credentials are found. If you need another user model, you can set up a lookup function under the ``HAWK_USER_LOOKUP`` setting. This function receives the request and the matched credentials dict as parameters and returns a ``(user, auth)`` tuple as per `custom authentication`_. For example, with a ``HawkUser`` model whose ``user_id`` is included in the credentials dict, you can write a function ``hawk_user_lookup`` as follows:

.. code-block:: python

    def hawk_user_lookup(request, credentials):
        return HawkUser.objects.get(some_id=credentials['id'])

and then you would configure it in your settings:

.. code-block:: python

    HAWK_USER_LOOKUP = 'yourapi.auth.hawk_user_lookup'

.. _`custom authentication`: http://www.django-rest-framework.org/api-guide/authentication/#custom-authentication

Alternately, you can subclass ``HawkAuthentication`` and override the ``hawk_user_lookup()`` method. For example:

.. code-block:: python

    from hawkrest import HawkAuthentication

    class YourHawk(HawkAuthentication):
        def hawk_user_lookup(self, request, credentials):
            return HawkUser.objects.get(some_id=credentials['id'])

and then specify your new class instead in the authentication backend list:

.. code-block:: python

    REST_FRAMEWORK = {
        'DEFAULT_AUTHENTICATION_CLASSES': (
            'yourapi.auth.YourHawk',
        ),
        ...
    }


This setting is the number of seconds until a Hawk message
expires:

.. code-block:: python

    HAWK_MESSAGE_EXPIRATION = 60

To `prevent replay attacks`_, Hawkrest uses the Django cache framework
for nonce lookups. You should configure Django with something
like `memcache`_ in production. By default, Django uses in-memory
caching and by default nonce checking will be activated. If you need to
*disable* it for some reason, set this:

.. code-block:: python

    USE_CACHE_FOR_HAWK_NONCE = False  # only disable this if you need to

.. _`memcache`: https://docs.djangoproject.com/en/dev/topics/cache/#memcached
.. _`prevent replay attacks`: https://mohawk.readthedocs.io/en/latest/usage.html#using-a-nonce-to-prevent-replay-attacks


.. _protecting-api-views:

Protecting API views with Hawk
==============================

To protect all API views with Hawk by default, put this in your settings:

.. code-block:: python

    REST_FRAMEWORK = {
        'DEFAULT_AUTHENTICATION_CLASSES': (
            'hawkrest.HawkAuthentication',
        ),
        'DEFAULT_PERMISSION_CLASSES': (
            'rest_framework.permissions.IsAuthenticated',
        ),
    }

To protect a specific view directly, define it like this:

.. code-block:: python

    from rest_framework.permissions import IsAuthenticated
    from rest_framework.views import APIView

    from hawkrest import HawkAuthentication

    class ExampleView(APIView):
        authentication_classes = (HawkAuthentication,)
        permission_classes = (IsAuthenticated,)

Verification tool
=================

Hawkrest ships with a management command you can use to verify your
own Hawk API or any other Hawk authorized resource.

Run this from a Django app with Hawkrest installed for more info::

    ./manage.py hawkrequest --help

If you had secured your Django app using the credentials dict with
key ``script-user`` you could test it out like this::

    ./manage.py hawkrequest --url http://127.0.0.1:8000/your/view \
                            --creds script-user -X POST -d foo=bar
