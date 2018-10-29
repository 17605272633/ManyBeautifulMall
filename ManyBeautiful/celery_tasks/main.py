# celery启动文件

from celery import Celery
import os

# 为celery使用django配置文件进行设置
# 类似于manage.py中添加指定路径
if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'ManyBeautifulMall.settings.dev'

# 创建celery应用
app = Celery('meiduo')

# 导入celery配置
app.config_from_object('celery_tasks.config')

# 自动识别任务
app.autodiscover_tasks([
    'celery_tasks.sms',
    'celery_tasks.email',
])









