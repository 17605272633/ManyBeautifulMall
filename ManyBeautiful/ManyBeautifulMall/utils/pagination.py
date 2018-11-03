from rest_framework.pagination import PageNumberPagination


# 分页配置
class SKUListPagination(PageNumberPagination):
    """分页配置类"""
    page_size = 5
    page_size_query_param = 'page_size'
    # max_page_size = 3

