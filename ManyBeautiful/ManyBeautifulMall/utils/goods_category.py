from collections import OrderedDict
from goods.models import GoodsCategory, GoodsChannel


def get_goods_category():
    """查询分类数据"""
    """
    {
        组编号(同一频道): {
            一级分类channels:[{手机},{相机},{数码}]
            二级分类sub_cats:[二级分类[三级分类]]
        }
        ......
    }
    """
    categories = OrderedDict()  # 定义一个有序字典
    channels = GoodsChannel.objects.order_by("group_id", "sequence")
    for channel in channels:
        # channel.group_id 组的编号
        # channel.category 一级分类
        # channel.url 一级分类的链接

        # 判断当前组id是否存在,使赋值只执行一次
        if channel.group_id not in categories:
            categories[channel.group_id] = {'channels': [], 'sub_cats': []}

        # 添加一级分类到有序列表
        categories[channel.group_id]['channels'].append({
            'id': channel.id,
            'name': channel.category.name,
            'url': channel.url
        })
        # 获取二级分类
        for sub_cats2 in channel.category.goodscategory_set.all():
            sub_cats2.sub_cats = []
            # 获取三级分类
            for sub_cats3 in sub_cats2.goodscategory_set.all():
                sub_cats2.sub_cats.append(sub_cats3)
            categories[channel.group_id]['sub_cats'].append(sub_cats2)

    return categories