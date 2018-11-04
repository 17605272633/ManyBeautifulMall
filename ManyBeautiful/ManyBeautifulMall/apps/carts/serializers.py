from rest_framework import serializers

from goods.models import SKU


# 购物车数据添加序列化器
class AddCartSerializer(serializers.Serializer):
    """购物车数据添加序列化器"""

    # 定义属性
    sku_id = serializers.IntegerField(label='sku_id', min_value=1)
    count = serializers.IntegerField(label='数量', min_value=1)
    selected = serializers.BooleanField(label='是否勾选', default=True)

    # 验证
    def validate(self, attrs):
        try:
            sku = SKU.objects.get(id=attrs['sku_id'])
        except:
            raise serializers.ValidationError('查询商品SKU错误')

        if sku is None:
            raise serializers.ValidationError('未查询到数据')
        else:
            return attrs


# 购物车数据查询序列化器
class FindCartSerializer(serializers.ModelSerializer):
    """购物车数据查询序列化器"""
    # 定义属性
    count = serializers.IntegerField(label='数量')
    selected = serializers.BooleanField(label='是否勾选')


# 购物车数据修改序列化器
class UpDateCartSerializer(serializers.Serializer):
    """购物车数据修改序列化器"""

    # 定义属性
    sku_id = serializers.IntegerField(label='sku_id', min_value=1)
    count = serializers.IntegerField(label='数量', min_value=1)
    selected = serializers.BooleanField(label='是否勾选', default=True)

    # 验证
    def validate(self, attrs):
        try:
            sku = SKU.objects.get(id=attrs['sku_id'])
        except:
            raise serializers.ValidationError('查询商品SKU错误')

        if sku is None:
            raise serializers.ValidationError('未查询到数据')
        else:
            return attrs


# 购物车数据删除序列化器
class DeleteCartSerializer(serializers.Serializer):
    """购物车数据删除序列化器"""
    # 定义属性
    sku_id = serializers.IntegerField(label='商品id', min_value=1)

    # 验证
    def validate_sku_id(self, value):
        # 获取商品信息,验证商品是否存在
        try:
            sku = SKU.objects.get(id=value)
        except SKU.DoesNotExist:
            raise serializers.ValidationError('商品不存在')

        return value




