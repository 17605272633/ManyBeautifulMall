import os
from collections import OrderedDict

from django.conf import settings
from django.shortcuts import render

from .models import ContentCategory, Content
from goods.models import GoodsCategory, GoodsChannel


# 首页静态化
def generate_index_html():
    """生成静态的主页html文件"""

    # 查询分类数据, 广告数据
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

    """查询广告数据"""
    contents = {}
    content_categories = ContentCategory.objects.all()
    for category in content_categories:
        # 拿到广告类别下所有启用的广告,并排序
        contents[category.key] = category.content_set.filter(status=True).order_by("sequence")

    # 生成html标签,写入html文件中
    """生成html字符串"""
    # render(request, template_name, context)
    response = render(None, 'index.html', {'categories': categories, 'contents': contents})
    html_str = response.content.decode()

    """写文件"""
    file_name = os.path.join(settings.GENERATED_STATIC_HTML_FILES_DIR, 'index.html')
    with open(file_name, 'w', encoding='utf-8') as f:
        f.write(html_str)

    print('OK')
