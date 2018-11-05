from django_redis import get_redis_connection
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from carts import constants
from carts.serializers import AddCartSerializer, FindCartSerializer, UpDateCartSerializer, DeleteCartSerializer, \
    SelectAllCartSerializer
from goods.models import SKU
from utils import myjson


# 购物车视图集
class CartView(APIView):
    """购物车视图集"""

    def perform_authentication(self, request):
        # 前端请求时携带了Authorization请求头（主要是JWT），而如果用户未登录，此请求头的JWT没有值，
        # 为了防止REST framework框架在验证此无意义的JWT时抛出401异常
        # 重写用户认证方法,不在进入视图前就检查JWT
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
            redis_cart_id = redis_conn.hkeys('cart_%s' % user.id)
            redis_cart_selected = redis_conn.smembers('cart_selected_%s' % user.id)
            print(redis_cart_selected)
            redis_cart_selected = [int(sku_id) for sku_id in redis_cart_selected]
            print(redis_cart_selected)

            # 查询商品
            skus = SKU.objects.filter(pk__in=redis_cart_id)
            # 为商品添加额外两个属性
            for sku in skus:
                sku.count = redis_conn.hget('cart_%s' % user.id, sku.id)
                sku.selected = sku.id in redis_cart_selected  # 在,则为True,不在则为False

        else:
            # 用户未登录，从cookie中读取
            cart_str = request.COOKIES.get('cart')
            if cart_str is not None:
                cart_dict = myjson.loads(cart_str)
            else:
                cart_dict = {}

            # 遍历处理购物车数据
            # 根据键,查询商品信息
            skus = []
            for key, value in cart_dict.items():
                sku = SKU.objects.get(pk=key)
                sku.count = value['count']
                sku.selected = value['selected']
                skus.append(sku)

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
        # 获取当前用户信息(并验证登陆)
        try:
            user = request.user
        except Exception:
            # 验证失败,用户数据为空
            user = None

        # 定义序列化器对象,并验证
        cart_serializer = AddCartSerializer(data=request.data)
        cart_serializer.is_valid(raise_exception=True)

        # 获取属性的值
        sku_id = cart_serializer.validated_data.get('sku_id')
        count = cart_serializer.validated_data.get('count')
        selected = cart_serializer.validated_data.get('selected')

        response = Response(cart_serializer.data, status=status.HTTP_201_CREATED)

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
            cart_str = request.COOKIES.get('cart')
            if cart_str is not None:
                # 不为空,将其解码并反序列化为python类型
                cart_dict = myjson.loads(cart_str)
            else:
                # 为空,返回空字典
                cart_dict = {}

            # 将数据以正确的格式添加
            cart_dict[sku_id] = {
                'count': count,
                'selected': selected
            }

            # 将cookie数据序列化为bytes类型并编码
            cookie_cart = myjson.dumps(cart_dict)

            # 设置购物车的cookie
            # 需要设置有效期，否则是临时cookie
            response.set_cookie('cart', cookie_cart, max_age=constants.CART_COOKIE_EXPIRES)

        return response

    def put(self, request):
        """
        修改购物车信息
        请求方式 ： PUT /cart/
        :param request: sku_id(商品sku id), count(数量), selected(是否勾选，默认勾选)
        :return: sku_id, count, selected
        """
        # 获取当前用户信息(并验证登陆)
        try:
            user = request.user
        except Exception:
            # 验证失败,用户数据为空
            user = None

        update_serializer = UpDateCartSerializer(data=request.data)
        update_serializer.is_valid(raise_exception=True)

        # 获取属性的值
        sku_id = update_serializer.validated_data.get('sku_id')
        count = update_serializer.validated_data.get('count')
        selected = update_serializer.validated_data.get('selected')

        response = Response(update_serializer.data)

        # 用户已登录，数据在redis中
        if user is not None and user.is_authenticated:

            redis_conn = get_redis_connection('cart')
            # 修改商品数量信息
            redis_conn.hset('cart_%s' % user.id, sku_id, count)
            # 修改商品是否勾选
            if selected is True:
                # 未勾选, 修改为勾选
                redis_conn.sadd('cart_selected_%s' % user.id, sku_id)
            else:
                # 已勾选, 修改为未勾选
                redis_conn.srem('cart_selected_%s' % user.id, sku_id)

        # 用户未登录,数据在cookie中
        else:

            # 获取请求中的cookie中的购物车数据
            cart_str = request.COOKIES.get('cart')
            if cart_str is not None:
                # 不为空,将其解码并反序列化为python类型
                cart_dict = myjson.loads(cart_str)
            else:
                # 为空,返回空字典
                cart_dict = {}

            cart_dict[sku_id] = {
                'count': count,
                'selected': selected
            }

            # 将cookie数据序列化为bytes类型并编码
            cookie_cart = myjson.dumps(cart_dict)

            # 设置购物车的cookie
            # 需要设置有效期，否则是临时cookie
            response.set_cookie('cart', cookie_cart, max_age=constants.CART_COOKIE_EXPIRES)

        return response

    def delete(self, request):
        """
        删除购物车信息
        :param request: request.data中有sku_id
        :return: 无, 有状态码
        """
        # 获取当前用户信息(并验证登陆)
        try:
            user = request.user
        except Exception:
            # 验证失败,用户数据为空
            user = None

        delete_serializer = DeleteCartSerializer(data=request.data)
        if delete_serializer.is_valid(raise_exception=True) is False:
            return Response(delete_serializer.errors)

        # 获取属性的值
        sku_id = delete_serializer.validated_data['sku_id']

        # 用户已登录，从redis中删除
        if user is not None and user.is_authenticated:

            redis_conn = get_redis_connection('cart')
            # 删除商品数量信息
            redis_conn.hdel('cart_%s' % user.id, sku_id)
            # 删除商品勾选信息
            redis_conn.srem('cart_selected_%s' % user.id, sku_id)

            response =  Response(status=status.HTTP_204_NO_CONTENT)
            return response

        # 用户未登录，从cookie中删除
        else:

            # 获取请求中的cookie中的购物车数据
            cart_str = request.COOKIES.get('cart')
            if cart_str is not None:
                # 不为空,将其解码并反序列化为python类型
                cart_dict = myjson.loads(cart_str)

                # 判断购物车数据列表中是否有该商品id,有则删除该键
                if sku_id in cart_dict:
                    del cart_dict[sku_id]
                    # 将cookie数据序列化为bytes类型并编码
                    cookie_cart = myjson.dumps(cart_dict)

                    # 设置响应数据
                    response = Response(status=status.HTTP_204_NO_CONTENT)

                    # 设置购物车的cookie
                    # 需要设置有效期，否则是临时cookie
                    response.set_cookie('cart', cookie_cart, max_age=constants.CART_COOKIE_EXPIRES)
                    return response

            else:
                # 购物车数据为空,则无数据可删除,直接返回
                response = Response(status=status.HTTP_204_NO_CONTENT)
                return response


# 购物车全选视图集
class CartSelectAllView(APIView):
    """购物车全选视图集"""

    def perform_authentication(self, request):
        # 前端请求时携带了Authorization请求头（主要是JWT），而如果用户未登录，此请求头的JWT没有值，
        # 为了防止REST framework框架在验证此无意义的JWT时抛出401异常
        # 重写用户认证方法,不在进入视图前就检查JWT
        pass

    def put(self, request):
        """
        购物车全选
        PUT /cart/selection/
        :param request: request.data中有selected(是否全选)
        :return: {"message": "ok"}
        """
        # 获取当前用户信息(并验证登陆)
        try:
            user = request.user
        except Exception:
            # 验证失败,用户数据为空
            user = None

        selall_serializer = SelectAllCartSerializer(data=request.data)
        selall_serializer.is_valid(raise_exception=True)

        # 获取属性的值
        selected = selall_serializer.validated_data['selected']

        if user is not None and user.is_authenticated:
            # 用户已登陆, 数据在redis中

            redis_conn = get_redis_connection('cart')

            # 获取所有商品sku_id
            sku_ids = redis_conn.hkeys('cart_%d' % request.user.id)

            # 判断是否全选
            if selected:
                # 全选
                redis_conn.sadd('cart_selected_%s' % user.id, *sku_ids)
            else:
                # 取消全选
                redis_conn.srem('cart_selected_%s' % user.id, *sku_ids)
            response = Response({'message': 'ok'})
            return response

        else:
            # 用户未登录，从cookie中删除

            # 获取请求中的cookie中的购物车数据
            cart_str = request.COOKIES.get('cart')
            if cart_str is not None:
                # 不为空,将其解码并反序列化为python类型
                cart_dict = myjson.loads(cart_str)

                # 获取商品id sku_id,修改勾选属性值为请求中的值
                for sku_id in cart_dict:
                    cart_dict[sku_id]['selected'] = selected

                # 将cookie数据序列化为bytes类型并编码
                cookie_cart = myjson.dumps(cart_dict)

                # 设置响应数据
                response = Response({'message': 'OK'})

                # 设置购物车的cookie
                # 需要设置有效期，否则是临时cookie
                response.set_cookie('cart', cookie_cart, max_age=constants.CART_COOKIE_EXPIRES)
                return response

            else:
                # 购物车数据为空,则无数据可删除,直接返回
                response = Response({'message': 'OK'})
                return response