from django.db import models


# 省市区数据表,使用自关联方式
class Area(models.Model):
    """行政区划"""
    name = models.CharField(max_length=20, verbose_name="名称")
    parent = models.ForeignKey('self',
                               on_delete=models.SET_NULL,
                               # 通过Area模型类对象.subs查询所有下属行政区划
                               related_name='subs',
                               null=True, blank=True,  # 允许为空,允许留白
                               verbose_name='上级行政区划')

    class Meta:
        db_table = 'tb_areas'
        verbose_name = '行政区划'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name
