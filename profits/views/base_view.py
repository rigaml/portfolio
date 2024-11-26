from rest_framework.viewsets import ModelViewSet
from rest_framework.exceptions import MethodNotAllowed

from profits.permissions import IsAdminOrReadOnly

class BaseViewSet(ModelViewSet):
    
    # permission_classes = [IsAdminOrReadOnly]
        
    def update(self, request, *args, **kwargs):
        raise MethodNotAllowed(request.method)

    def partial_update(self, request, *args, **kwargs):
        raise MethodNotAllowed(request.method)    