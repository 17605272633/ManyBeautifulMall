from django_redis import get_redis_connection
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.core.handlers.exception import logger
from goods.models import SKU
from django.utils import timezone
from django.db import transaction
from decimal import Decimal

# 购物车商品序列化器
from orders.models import OrderInfo, OrderGoods
from users.models import Address


class CartSKUSerializer(serializers.ModelSerializer):
    """购物车商品序列化器"""

    # 添加属性
    count = serializers.IntegerField(label="数量")

    class Meta:
        model = SKU
        fields = ('id', 'name', 'default_image_url', 'price', 'count')


# 订单结算数据序列化器
class OrderSettlementSerializer(serializers.Serializer):
    """订单结算数据序列化器"""
    freight = serializers.DecimalField(label='运费', max_digits=10, decimal_places=2)
    skus = CartSKUSerializer(many=True)


"""
返回的json对象格式
{
    "freight":"运费",
    "skus":[   结算的商品列表  
        {
            "id":  商品id,
            "name":  商品名称,
             "default_image_url":  商品默认图片路径,
            "price":  商品单价,
            "count":  商品数量
        },
        ......
    ]
}
"""


# 下单数据序列化器
class SaveOrderSerializer(serializers.Serializer):
    """下单数据序列化器"""
    """定义属性"""
    order_id = serializers.CharField(read_only=True)
    address = serializers.IntegerField(write_only=True)
    pay_method = serializers.IntegerField(write_only=True)

    # class Meta:
    #     model = OrderInfo
    #     fields = ('order_id', 'address', 'pay_method')
    #     read_only_fields = ('order_id',)
    #     extra_kwargs = {
    #         'address': {
    #             'write_only': True,
    #             'required': True,
    #         },
    #         'pay_method': {
    #             'write_only': True,
    #             'required': True
    #         }
    #     }

    """验证"""
    def validated_address(self, value):
        count = Address.objects.filter(pk=value).count()
        if count <= 0:
            raise ValidationError("无效的收货地址")
        return value

    def validated_pay_method(self, value):
        if value not in [1, 2]:
            raise ValidationError("无效的付款方式")
        return value

    """创建"""
    def create(self, validated_data):
        """保存订单"""
        # 获取当前下单用户数据
        user = self.context['request'].user

        # 生成订单编号  日期+user.id
        # timezone.now() -> datetime
        order_id = timezone.now().strftime('%Y%m%d%H%M%S') + ('%09d' % user.id)
        # 保存订单基本数据
        address = validated_data.get('address')
        pay_method = validated_data.get("pay_method")

        # 生成订单数据  在事务中
        with transaction.atomic():

            # 创建保存点
            save_id = transaction.savepoint()

            # 保存订单信息
            try:
                # 创建订单信息
                order = OrderInfo()
                order.order_id = order_id  # 订单标号
                order.user = user  # 下单用户
                order.address = Address.objects.get(pk=address)  # 收获地址
                order.total_count = 0  # 商品总数
                order.total_amount = Decimal(0)  # 商品总金额
                order.freight = Decimal(10)  # 运费
                order.pay_method = pay_method  # 支付方式
                order.status = OrderInfo.ORDER_STATUS_ENUM['UNSEND'] \
                    if pay_method == OrderInfo.PAY_METHODS_ENUM['CASH'] \
                    else OrderInfo.ORDER_STATUS_ENUM['UNPAID']  # 订单状态
                order.save()

                # 获取购物车信息
                redis_conn = get_redis_connection("cart")
                redis_cart = redis_conn.hgetall("cart_%s" % user.id)
                cart_selected = redis_conn.smembers('cart_selected_%s' % user.id)

                # 将bytes类型转换为int类型
                cart_count = {}
                """
                {
                    sku_id1 : count1,
                    sku_id2 : count2,
                }
                """
                for sku_id in cart_selected:
                    cart_count[int(sku_id)] = int(redis_cart[sku_id])

                # # 一次查询出所有商品数据
                # skus = SKU.objects.filter(id__in=cart_count.keys())

                # 订单信息处理
                # 获取所有商品id
                sku_id_list = cart_count.keys()

                for sku_id in sku_id_list:
                    while True:
                        # 获取当前商品信息
                        sku = SKU.objects.get(id=sku_id)

                        # 获取订单中当前商品数量,库存,销量
                        sku_count = cart_count[sku.id]

                        origin_stock = sku.stock  # 原始库存
                        origin_sales = sku.sales  # 原始销量

                        # 判断商品库存是否充足
                        if sku_count > origin_stock:
                            # 不足, 回滚到保存点
                            transaction.savepoint_rollback(save_id)
                            raise ValidationError('商品库存不足')

                        # 充足, 减少商品库存，增加商品销量
                        new_stock = origin_stock - sku_count
                        new_sales = origin_sales + sku_count

                        # 乐观锁
                        # 根据原始库存条件更新,更新成功则返回跟新条目,更新失败则跳出本次循环
                        ret = SKU.objects.filter(id=sku.id, stock=origin_stock).update(stock=new_stock, sales=new_sales)
                        if ret == 0:
                            continue

                        # 累加商品的SPU销量信息
                        sku.goods.sales += sku_count
                        sku.goods.save()

                        # # 记录订单基本信息的数据
                        # order.total_count += sku_count  # 累计总金额
                        # order.total_amount += (sku.price * sku_count)  # 累计总额

                        # 保存订单商品
                        OrderGoods.objects.create(
                            order=order,
                            sku=sku,
                            count=sku_count,
                            price=sku.price,
                        )

                        # 更新成功,结束循环
                        break

                # 更新订单的金额数量信息
                # 记录订单基本信息的数据
                order.total_count += sku_count  # 累计总金额
                order.total_amount += (sku.price * sku_count)  # 累计总额
                order.total_amount += order.freight
                order.save()

            except ValidationError:
                raise
            except Exception as e:
                logger.error(e)
                # 回滚到保存点
                transaction.savepoint_rollback(save_id)
                raise

            # 提交事务
            transaction.savepoint_commit(save_id)

            # 更新redis中保存的购物车数据
            redis_conn.hdel('cart_%s' % user.id, *cart_selected)
            redis_conn.srem('cart_selected_%s' % user.id, *cart_selected)

            return order
