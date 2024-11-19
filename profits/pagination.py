from rest_framework.pagination import LimitOffsetPagination

class DefaultPagination(LimitOffsetPagination):
    default_limit = 10
    max_limit= 100

    def paginate_queryset(self, queryset, request, view=None):
        """
        Enforce default pagination if no parameters are provided
        """
        limit = request.query_params.get('limit')
        offset = request.query_params.get('offset', 0)

        if limit is None:
            limit = self.default_limit
            offset = 0
            # Modify query_params to reflect defaults for consistency
            request.query_params._mutable = True
            request.query_params['limit'] = str(limit)
            request.query_params['offset'] = str(offset)
            request.query_params._mutable = False        

        return super().paginate_queryset(queryset, request, view)