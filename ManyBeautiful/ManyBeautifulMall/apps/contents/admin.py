from django.contrib import admin
from . import models

# 注册模型类
admin.site.register(models.ContentCategory)
admin.site.register(models.Content)






