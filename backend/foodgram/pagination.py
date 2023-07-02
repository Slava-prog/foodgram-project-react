from rest_framework.pagination import PageNumberPagination

class PageLimitPagination(PageNumberPagination):
    page_query_param = 'page'
    page_size_query_param = 'limit'