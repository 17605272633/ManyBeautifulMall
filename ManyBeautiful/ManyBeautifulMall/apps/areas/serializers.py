from rest_framework import serializers
from .models import Area


# 行政区域信息序列化器
class AreaSerializer(serializers.ModelSerializer):
    """行政区域信息序列化器"""

    class Meta:
        model = Area
        fields = ('id', 'name')


# 子行政区划信息序列化器
class SubAreaSerializer(serializers.ModelSerializer):
    """子行政区划信息序列化器"""
    # 关系属性默认输出对应的pk,可指定为输出对应的序列化器
    subs = AreaSerializer(many=True, read_only=True)

    class Meta:
        model = Area
        fields = ('id', 'name', 'subs')










