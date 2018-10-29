from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework_extensions.cache.mixins import CacheResponseMixin
from areas.models import Area
from areas.serializers import AreaSerializer, SubAreaSerializer


# 行政区划信息类视图
class AreasViewSet(ReadOnlyModelViewSet, CacheResponseMixin):
    """行政区划信息"""

    # 设置不分页
    pagination_class = None

    # 当前请求方式对应的处理函数名为 list 和 retrieve

    def get_queryset(self):
        """指定视图使用的查询集"""
        if self.action == 'list':  # action 指定请求方式于处理函数的对应关系
            return Area.objects.filter(parent=None)
        else:
            return Area.objects.all()

    def get_serializer_class(self):
        """指定序列化器"""
        if self.action == 'list':
            return AreaSerializer
        else:
            return SubAreaSerializer








