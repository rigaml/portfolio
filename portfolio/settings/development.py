#
# Settings for Development environment
#
import os
from .base import *
from portfolio import logging_config

logging_config.LOGGING['handlers']['file']['filename'] = Path(BASE_DIR) / 'logs' / 'portfolio.log'

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-dev-key')
DEBUG = True

ALLOWED_HOSTS = ['dev-api.rigaml-change-aws.com', 'localhost', '127.0.0.1']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'portfoliodb'),
        'USER': os.environ.get('DB_USER', 'portfoliouser'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'dummypassword'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# Basic cache configuration
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}