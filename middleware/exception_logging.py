import logging


class ExceptionLoggingMiddleware:
    """
    Middleware to catch and log unhandled exception.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            return self.get_response(request)
        except Exception as e:
            logger = logging.getLogger('django.request')
            logger.exception(f"Unhandled exception: {e}")
            raise