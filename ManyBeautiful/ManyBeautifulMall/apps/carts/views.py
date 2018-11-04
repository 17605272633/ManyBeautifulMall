import base64
import pickle

from django_redis import get_redis_connection
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from carts import constants
from carts.serializers import AddCartSerializer, FindCartSerializer, UpDateCartSerializer
from goods.models import SKU


class CartView(APIView):
    """购物车视图函数"""

    # 前端请求时携带了Authorization请求头（主要是JWT），而如果用户未登录，此请求头的JWT没有值，
    # 为了防止REST framework框架在验证此无意义的JWT时抛出401异常
    # 重写用户认证方法,不在进入视图前就检查JWT
    def perform_authentication(self, request):
        pass

    def get(self, request):
        """
        获取购物车信息
        请求方式 ： GET /cart/
        :param request: request.user 当前用户
        :return: id, count, selected, name, default_image_url, price
                 也就是商品的各个数据
        """
        # 获取用户, 判断用户登录
        try:
            user = request.user
        except Exception:
            user = None

        if user is not None and user.is_authenticated:
            # 用户登录,数据从redis中取出
            redis_conn = get_redis_connection('cart')
            # 获取redis中存储的信息
            redis_cart = redis_conn.hgetall('cart_%s' % user.id)
            redis_cart_selected = redis_conn.smembers('cart_selected_%s' % user.id)

            # 定义字典,存入购物车数据
            cart = {}
            for sku_id, count in redis_cart.items():
                cart[int(sku_id)] = {
                    'count': int(count),
                    'selected': sku_id in redis_cart_selected
                }

        else:
            # 用户未登录，从cookie中读取
            cart = request.COOKIES.get('cart')
            if cart is not None:
                cart = pickle.loads(base64.b64decode(cart.encode()))
            else:
                cart = {}

        # 遍历处理购物车数据
        # 根据键,查询商品信息
        skus = SKU.objects.filter(id__in=cart.keys())
        for sku in skus:
            # 设置skus中每一条商品的数量和是否勾选
            sku.count = cart[sku.id]['count']
            sku.selected = cart[sku.id]['selected']

        # 序列化数据并返回
        find_serializer = FindCartSerializer(skus, many=True)
        return Response(find_serializer.data)

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
        cart_serializer = AddCartSerializer(data=request.data)
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
                # 默认勾选
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

            # 如果cookie中的cart存储了商品信息,则使用其数量数据
            sku = cart.get(sku_id)
            if sku:
                # 有商品,获取此商品数量并转化为int类型
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

    def put(self, request):
        """
        修改购物车信息
        请求方式 ： PUT /cart/
        :param request: sku_id(商品sku id), count(数量), select(是否勾选，默认勾选)
        :return: sku_id, count, selected
        """
        update_serializer = UpDateCartSerializer(data=request.data)
        if update_serializer.is_valid(raise_exception=True) is False:
            return Response(update_serializer.errors)

        # 获取属性的值
        sku_id = update_serializer.validated_data.get('sku_id')
        count = update_serializer.validated_data.get('count')
        selected = update_serializer.validated_data.get('selected')

        # 获取当前用户信息(并验证登陆)
        try:
            user = request.user
        except Exception:
            # 验证失败,用户数据为空
            user = None

        # 用户已登录，数据在redis中
        if user is not None and user.is_authenticated:

            redis_conn = get_redis_connection('cart')
            # 修改商品数量信息
            redis_conn.hset('cart_%s' % user.id, sku_id, count)
            # 修改商品是否勾选
            if selected:
                # 未勾选, 修改为勾选
                redis_conn.sadd('cart_selected_%s' % user.id, sku_id)
            else:
                # 已勾选, 修改为未勾选
                redis_conn.srem('cart_selected_%s' % user.id, sku_id)

            return Response(update_serializer.data)

        # 用户未登录,数据在cookie中
        else:

            # 获取请求中的cookie中的购物车数据
            cart = request.COOKIES.get('cart')
            if cart is not None:
                # 不为空,将其解码并反序列化为python类型
                cart = pickle.loads(base64.b64decode(cart.encode()))
            else:
                # 为空,返回空字典
                cart = {}

            cart[sku_id] = {
                'count': count,
                'selected': selected
            }

            # 将cookie数据序列化为bytes类型并编码
            cookie_cart = base64.b64encode(pickle.dumps(cart)).decode()

            response = Response(update_serializer.data)

            # 设置购物车的cookie
            # 需要设置有效期，否则是临时cookie
            response.set_cookie('cart', cookie_cart, max_age=constants.CART_COOKIE_EXPIRES)
            return response
