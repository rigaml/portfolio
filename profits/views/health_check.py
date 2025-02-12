from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import connections
from django.db.utils import OperationalError

@api_view(['GET'])
def health_check(request):
    """
    Test database connection.
    """
    try:
        connections['default'].cursor()
        return Response({"status": "healthy"})
    except OperationalError:
        return Response({"status": "unhealthy"}, status=503)