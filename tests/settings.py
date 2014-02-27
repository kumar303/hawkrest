#
# Hawkrest settings
#

# When True, it means Hawk authentication will be disabled everywhere.
# This is mainly just to get a speed-up in an app while testing.
SKIP_HAWK_AUTH = False

HAWK_CREDENTIALS = {
    'script-user': {
        'id': 'script-user',
        'key': 'some really long secret',
        'algorithm': 'sha256'
    },
}

# Number of seconds until a Hawk message expires.
HAWK_MESSAGE_EXPIRATION = 60

# When True, use the Django cache framework for checking Hawk nonces.
# Django must already be configured to use some kind of caching backend.
USE_CACHE_FOR_HAWK_NONCE = True

#
# Django settings
#

SECRET_KEY = 'not real, just for tests'
DEBUG = False
TEMPLATE_DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'hawkrest-tests'
    }
}

INSTALLED_APPS = (
    'django_nose',
    'hawkrest',
)

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

NOSE_PLUGINS = [
    'nosenicedots.plugin.NiceDots',
]

NOSE_ARGS = [
    '--logging-clear-handlers',
    '--with-nicedots',
]

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'hawkrest.HawkAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.AllowAny',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'rest_framework.filters.DjangoFilterBackend',
    ),
    'PAGINATE_BY': 20,
    'PAGINATE_BY_PARAM': 'limit'
}
