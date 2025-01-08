#####
# Settings for local development
#####

# Importing all the settings defined in base
from .base import *

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-&!2a^)8p7i#5*422cvyo5$vwk91)_wy&ri&%+q23oe_^#m899p'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'portfoliodb',
        'USER': 'portfoliouser',
        'PASSWORD': 'dummypassword',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Enable Django Debug Toolbar
INSTALLED_APPS = ['debug_toolbar'] + INSTALLED_APPS

# Enable Django Debug Toolbar
MIDDLEWARE = ['debug_toolbar.middleware.DebugToolbarMiddleware'] + MIDDLEWARE
INTERNAL_IPS = ['127.0.0.1']

# Disable logging in local development
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}