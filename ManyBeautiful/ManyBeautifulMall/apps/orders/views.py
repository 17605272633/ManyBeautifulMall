from django_redis import get_redis_connection
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from decimal import Decimal
from goods.models import SKU
from orders.serializers import OrderSettlementSerializer, SaveOrderSerializer


# 订单结算类视图
class OrderSettlementView(APIView):
    """订单结算类视图"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        订单结算
        GET /orders/settlement/
        :param request: request.user当前用户
        :return: {
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

        # 获取登陆的用户数据
        user = request.user

        # 获取购物车中被勾选的要结算的商品信息
        redis_conn = get_redis_connection('cart')
        # redis_cart_id = redis_conn.hkeys('cart_%s' % user.id)  # 拿到当前用户所有购物车商品息
        redis_cart_selected = redis_conn.smembers('cart_selected_%s' % user.id)
        redis_cart_selected = [int(sku_id) for sku_id in redis_cart_selected]  # 拿到被勾选的商品sku_id

        # 拿到商品对应数量
        cart_count = {}
        """
        {
            sku_id1 : count1,
            sku_id2 : count2,
            ...
        }
        """
        for sku_id in redis_cart_selected:
            # hget key field
            cart_count[sku_id] = int(redis_conn.hget('cart_%s' % user.id, sku_id))

        # 查询商品,添加数量属性
        skus = SKU.objects.filter(pk__in=redis_cart_selected)
        for sku in skus:
            sku.count = cart_count[sku.id]

        # 运费
        freight = Decimal('10.00')

        # 定义序列化数据格式
        context = {
            'freight': freight,
            'skus': skus
        }

        serializer = OrderSettlementSerializer(context)
        return Response(serializer.data)


# 订单保存类视图
class SaveOrderView(CreateAPIView):
    """订单保存类视图"""
    permission_classes = [IsAuthenticated]
    serializer_class = SaveOrderSerializer






