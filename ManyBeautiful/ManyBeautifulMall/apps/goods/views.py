from drf_haystack.viewsets import HaystackViewSet
from rest_framework.generics import ListAPIView
from rest_framework.filters import OrderingFilter
from utils.pagination import SKUListPagination
from .serializers import SKUSerializer, SKUIndexSerializer
from .models import SKU


# 商品详情页类视图
class SKUListView(ListAPIView):
    """
    商品详情页
    访问路径: /categories/(?P<category_id>\d+)/skus/?page=xxx&page_size=xxx&ordering=xxx
    :return: count, next, previous, results, id, name, price, default_iamge,-url, comments
    """

    # queryset = SKU.objects.all()
    # 因为获取的是每个对象的详细数据,所以不能用原本的查询集方法
    # 重写获取查询集方法  self.kwargs===>是字典,用来获取获取路径中的参数
    def get_queryset(self):
        return SKU.objects.filter(category_id=self.kwargs['category_id'])

    serializer_class = SKUSerializer

    # 分页
    pagination_class = SKUListPagination

    # 排序
    filter_backends = [OrderingFilter]
    ordering_fields = ['create_time', 'price', 'sales']


# SKU搜索视图集
class SKUSearchViewSet(HaystackViewSet):
    """SKU搜索"""

    # 模型类可改
    index_models = [SKU]

    serializer_class = SKUIndexSerializer

    # 分页
    pagination_class = SKUListPagination

    """
    返回结果实例:
    {
        "count": 10,
        "next": "http://api.meiduo.site:8000/skus/search/?page=2&text=%E5%8D%8E",
        "previous": null,
        "results": [
            {
                "text": "华为 HUAWEI P10 Plus 6GB+64GB 钻雕金 移动联通电信4G手机 双卡双待\nwifi双天线设计！徕卡人像摄影！P10徕卡双摄拍照，低至2988元！\n9",
                "id": 9,
                "name": "华为 HUAWEI P10 Plus 6GB+64GB 钻雕金 移动联通电信4G手机 双卡双待",
                "price": "3388.00",
                "default_image_url": "http://10.211.55.5:8888/group1/M00/00/02/CtM3BVrRcUeAHp9pAARfIK95am88523545",
                "comments": 0
            },
            ...
        ]
    }
    """
