#!/usr/bin/env python
# #!/home/python/.virtualenvs/py3_django_1.11/bin/python
# 指定执行此py文件的执行解释器为python
# /usr/bin/env表示在当前环境中查找python命令
"""
功能：手动生成所有SKU的静态detail html文件
使用方法:
    ./generate_detail_html.py
"""
import sys
import os
import django

# 设置环境变量
sys.path.insert(0, '../')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ManyBeautifulMall.settings.dev")
django.setup()


from goods.models import SKU
from celery_tasks.html.tasks import generate_static_sku_detail_html

if __name__ == '__main__':
    skus = SKU.objects.all()
    for sku in skus:
        print(sku.id)
        generate_static_sku_detail_html(sku.id)
