from rest_framework.generics import ListAPIView
from rest_framework.filters import OrderingFilter
from utils.pagination import SKUListPagination
from .serializers import SKUSerializer
from .models import SKU


class SKUListView(ListAPIView):
    """sku列表数据"""
    # 因为获取的是每个对象的详细数据,所以不能用原本的查询集方法
    # 重写获取查询集方法  self.kwargs===>字典
    def get_queryset(self):
        return SKU.objects.filter(category_id=self.kwargs['category_id'])

    serializer_class = SKUSerializer

    # 分页
    pagination_class = SKUListPagination

    # 排序
    filter_backends = [OrderingFilter]
    ordering_fields = ['create_time', 'price', 'sales']
