from rest_framework import pagination


class GeneralCustomPagination(pagination.PageNumberPagination):
    """General paginator for most endpoints."""
    page_size = 6
    page_size_query_param = 'limit'
    page_query_param = 'page'
