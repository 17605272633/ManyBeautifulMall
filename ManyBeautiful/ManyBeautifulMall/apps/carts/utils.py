from django_redis import get_redis_connection

from utils import myjson


def merge_cart_cookie_to_redis(request, user_id, response):
    """
    合并购物车数据到redis中
    :param request: 用于读取cookie信息
    :param user: 当前登陆用户
    :param response: 响应对象,清除cookie数据
    :return:
    """
    # 获取cookie中购物车信息
    cart_str = request.COOKIES.get("cart")
    # 若为空,则直接返回响应
    if not cart_str:
        return response

    # 拿到字典类型的cookie中购物车数据
    cookie_cart_dict = myjson.loads(cart_str)

    # 定义字典,用于向redis中保存数据
    redis_cart_dict = {}

    # 记录redis勾选状态的sku_id
    redis_cart_selected_add = []  # 添加sku_id列表
    redis_cart_selected_remove = []  # 删除sku_id列表

    # 获取redis连接
    redis_conn = get_redis_connection("cart")
    redis_pip = redis_conn.pipeline()

    # 合并cookie购物车与redis购物车，保存到redis_cart_dict字典中
    for sku_id, count_select_dict in cookie_cart_dict.items():
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
        # 处理商品数量
        redis_cart_dict[sku_id] = count_select_dict['count']

        # 处理勾选状态,若勾选,则向添加列表中添加sku_id,反之则向删除列表中添加sku_id
        if count_select_dict['selected']:
            redis_cart_selected_add.append(sku_id)
        else:
            redis_cart_selected_remove.append(sku_id)

    # 如果添加完以后redis_cart_dict中有数据,则向redis中存储
    if redis_cart_dict:
        redis_pip.hmset('cart_%s' % user_id, redis_cart_dict)

        if redis_cart_selected_add:
            redis_pip.sadd('cart_selected_%s' % user_id, *redis_cart_selected_add)
        if redis_cart_selected_remove:
            redis_pip.srem('cart_selected_%s' % user_id, *redis_cart_selected_remove)

    redis_pip.execute()

    # 删除cookie中存储的信息
    # response.delete_cookie('cart')
    response.set_cookie('cart', 0, max_age=0)

    return response








