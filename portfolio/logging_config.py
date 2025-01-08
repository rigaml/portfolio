from datetime import datetime
from django.conf import settings

# Base logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'json': {
            'format': '{"time":"%(asctime)s","level":"%(levelname)s","message":"%(message)s","module":"%(module)s"}',
            'class': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'json',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/django/portfolio.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'profits': {  # Your app's logger
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# Production-specific logging configuration
if not settings.DEBUG:
    # Add CloudWatch handler
    LOGGING['handlers']['watchtower'] = {
        'class': 'watchtower.CloudWatchLogHandler',
        'log_group': '/ecs/portfolio',
        'stream_name': datetime.now().strftime('%Y-%m-%d'),
        'formatter': 'json',
        'use_queues': True,
        'create_log_group': False,
    }
    
    # Add CloudWatch handler to all loggers
    for logger in LOGGING['loggers'].values():
        logger['handlers'].append('watchtower')