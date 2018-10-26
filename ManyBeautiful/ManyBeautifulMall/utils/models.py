from django.db import models


class BaseModel(models.Model):
    """为模型类补充字段的模型基类"""
    create_time = models.DateField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        # db_table 为空,不创建表,该类只用于继承,为抽象的类
        abstract = True








