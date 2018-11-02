from drf_haystack.serializers import HaystackSerializer
from rest_framework import serializers
from .models import SKU
from .search_indexes import SKUIndex


# 商品详情页序列化器
class SKUSerializer(serializers.ModelSerializer):
    """商品详情页序列化器"""

    class Meta:
        model = SKU
        fields = ['id', 'name', 'price', 'default_image_url', 'comments']


# 索引结果序列化器
class SKUIndexSerializer(HaystackSerializer):
    """
    索引结果序列化器
    检查前端传入的参数text，并且检索出数据后再使用这个序列化器返回给前端
    """

    # 向前端返回数据时序列化的字段
    # Haystack通过Elasticsearch检索出搜索结果后，
    # 会在数据库中取出完整的数据库模型类对象，放到object中
    # 序列化器可改
    object = SKUSerializer(read_only=True)

    class Meta:
        # 索引类名称可改
        index_classes = [SKUIndex]
        fields = (
            'text',  # 用于接收查询关键字
            'object'  # 用于返回查询结果
        )

        """
        返回结果实例:
        {
            "text": "华为 HUAWEI P10 Plus 6GB+128GB 钻雕蓝 移动联通电信4G手机 双卡双待\nwifi双天线设计！徕卡人像摄影！P10徕卡双摄拍照，低至2988元！\n11",
            "object": {
                "id": 11,
                "name": "华为 HUAWEI P10 Plus 6GB+128GB 钻雕蓝 移动联通电信4G手机 双卡双待",
                "price": "3788.00",
                "default_image_url": "http://image.meiduo.site:8888/group1/M00/00/02/CtM3BVrRdG6AYdapAAcPaeOqMpA1594598",
                "comments": 2
            }
        },
        """
