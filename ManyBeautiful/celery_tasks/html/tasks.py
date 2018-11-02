import os

from django.conf import settings
from django.shortcuts import render

from celery_tasks.main import app
from goods.models import SKU
from utils.goods_category import get_goods_category


@app.task(name='generate_static_sku_detail_html')
def generate_static_sku_detail_html(sku_id):
    """
    生成商品详情页的静态页面
    :param sku_id: 商品的SKU id
    """

    # 商品分类菜单
    categories = get_goods_category()

    # 根据商品的sku_id获取当前sku信息
    sku = SKU.objects.get(id=sku_id)
    sku.images = sku.skuimage_set.all()

    # 导航信息中的频道
    goods = sku.goods
    goods.channel = goods.category1.goodschannel_set.all()[0]  # TODO ?

    # 构建当前函数的规格键的列表
    # sku_key = [规格1参数id， 规格2参数id， 规格3参数id, ...]
    # 获取SKU具体规格数据
    sku_specs = sku.skuspecification_set.order_by('spec_id')
    sku_key = []
    for spec in sku_specs:  # 向列表中添加规格的键的id
        sku_key.append(spec.option.id)

    # 获取当前商品的所有SKU
    skus = goods.sku_set.all()

    # 构建不同规格参数（选项）的sku字典
    """
    spec_sku_map = {
        (规格1参数id, 规格2参数id, 规格3参数id, ...): sku_id,
        (规格1参数id, 规格2参数id, 规格3参数id, ...): sku_id,
        ...
    }
    """
    spec_sku_map = {}

    for s in skus:
        # 获取sku对应的具体规格
        s_specs = s.skuspecification_set.order_by('spec_id')

        # 拿到对应着每一个规格的id,作为键并放入列表
        # 用于形成规格参数-sku字典的键
        key = []
        for spec in s_specs:
            key.append(spec.option.id)

        # 向规格参数-sku字典添加记录
        spec_sku_map[tuple(key)] = s.id

    # 获取当前商品的规格信息
    """
    specs = [
       {
           'name': '屏幕尺寸',
           'options': [
               {'value': '13.3寸', 'sku_id': xxx},
               {'value': '15.4寸', 'sku_id': xxx},
           ]
       },
       {
           'name': '颜色',
           'options': [
               {'value': '银色', 'sku_id': xxx},
               {'value': '黑色', 'sku_id': xxx}
           ]
       },
       ...
    ]
    """
    # 按照id排序获取商品规格
    specs = goods.goodsspecification_set.order_by('id')

    # 若当前sku的规格信息不完整，则不再继续
    if len(sku_key) < len(specs):  # 如果规格键数小于规格数,则视为信息不完整
        return

    for index, spec in enumerate(specs):  # enumerate: 转化成键值对,键为索引1,2,...
        # 获取当前sku的所有规格键
        key = sku_key[:]

        # 该规格的选项
        options = spec.specificationoption_set.all()
        for option in options:
            # 根据option.id获取对应的规格键
            key[index] = option.id
            # 根据规格键,在规格参数sku字典中查找符合当前规格的sku
            option.sku_id = spec_sku_map.get(tuple(key))

        # 设置规格的选项
        spec.options = options

    # 渲染模板, 生成静态html文件
    context = {
        'categories': categories,
        'goods': goods,
        'specs': specs,
        'sku': sku
    }
    # 生成html标签,写入html文件中
    # 生成html字符串
    # render(request, template_name, context)
    response = render(None, 'detail.html', context)
    html_str = response.content.decode()

    # 写文件
    file_path = os.path.join(settings.GENERATED_STATIC_HTML_FILES_DIR, 'goods/' + str(sku_id) + '.html')
    with open(file_path, 'w') as f:
        f.write(html_str)
