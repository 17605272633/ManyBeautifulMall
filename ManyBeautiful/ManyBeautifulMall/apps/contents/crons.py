import os
from collections import OrderedDict

from django.conf import settings
from django.shortcuts import render

from utils.goods_category import get_goods_category
from .models import ContentCategory, Content
from goods.models import GoodsCategory, GoodsChannel


# 首页静态化
def generate_index_html():
    """生成静态的主页html文件"""

    """查询分类数据"""
    categories = get_goods_category()

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
