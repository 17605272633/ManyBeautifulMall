import base64
import pickle

from django_redis import get_redis_connection
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from carts import constants
from carts.serializers import CartSerializer


class CartView(APIView):
    """购物车视图函数"""

    # 前端请求时携带了Authorization请求头（主要是JWT），而如果用户未登录，此请求头的JWT没有值，
    # 为了防止REST framework框架在验证此无意义的JWT时抛出401异常
    # 重写用户认证方法,不在进入视图前就检查JWT
    def perform_authentication(self, request):
        pass

    def post(self, request):
        """
        添加购物车信息
        请求方式: POST /cart/
        :param request: request.data中包含sku_id(商品sku id),
                                        count(数量),
                                        selected(是否勾选，默认勾选)
        :return: sku_id, count, selected
        """
        # 定义序列化器对象,并验证
        cart_serializer = CartSerializer(data=request.data)
        if cart_serializer.is_valid(raise_exception=True) is False:
            return Response(cart_serializer.errors)

        # 获取属性的值
        sku_id = cart_serializer.validated_data.get('sku_id')
        count = cart_serializer.validated_data.get('count')
        selected = cart_serializer.validated_data.get('selected')

        # 获取当前用户信息(并验证登陆)
        try:
            user = request.user
        except Exception:
            # 验证失败,用户数据为空
            user = None

        # 若用户不为空且已登录
        if user is not None and user.is_authenticated:
            # 用户登录,将数据保存到redis中

            redis_conn = get_redis_connection('cart')
            # 使用hash记录购物车商品数量
            redis_conn.hset('cart_%s' % user.id, sku_id, count)
            # 使用set记录是否勾选
            if selected:
                # 已勾选
                redis_conn.sadd('cart_selected_%s' % user.id, sku_id)

            return Response(cart_serializer.data, status=status.HTTP_201_CREATED)

        # 用户未登录,将数据保存到cookie中
        else:
            """
            cookie中数据保存格式
            {
                sku_id: {
                    "count": xxx,  // 数量
                    "selected": True  // 是否勾选
                },
                ...
            }
            """
            # 获取请求中的cookie中的购物车数据
            cart = request.COOKIES.get('cart')
            if cart is not None:
                # 不为空,将其解码并反序列化为python类型
                cart = pickle.loads(base64.b64decode(cart.encode()))
            else:
                # 为空,返回空字典
                cart = {}

            # 获取商品sku数据
            sku = cart.get(sku_id)
            if sku:
                # 有商品,获取此商品数量
                count = int(sku.get('count'))

            # 将数据以正确的格式保存
            cart[sku_id] = {
                'count': count,
                'selected': selected
            }

            # 将cookie数据序列化为bytes类型并编码
            cookie_cart = base64.b64encode(pickle.dumps(cart)).decode()

            response = Response(cart_serializer.data, status=status.HTTP_201_CREATED)

            # 设置购物车的cookie
            # 需要设置有效期，否则是临时cookie
            response.set_cookie('cart', cookie_cart, max_age=constants.CART_COOKIE_EXPIRES)
            return response



