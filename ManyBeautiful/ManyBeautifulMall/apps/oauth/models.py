from django.db import models
from utils.models import BaseModel


class OAuthQQUser(BaseModel):
    """QQ身份（openid）与用户模型类User的关联关系"""
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, verbose_name="用户")
    openid = models.CharField(max_length=64, verbose_name='openid', db_index=True)  # db_index为此字段创建索引

    class Meta:
        db_table = 'tb_oauth_qq'
        verbose_name = 'QQ登陆用户数据'
        verbose_name_plural = verbose_name










