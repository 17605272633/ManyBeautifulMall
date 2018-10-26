from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.


# AbstractUser: django自带的用户模型类,提供了以下定义好的字段
# username(用户名), first_name, last_name, email, password, groups,
# user_permissions, is_staff(访问Admin 站点), is_active(账号是否激活),
# is_superuser, last_login, date_joined(创建的时间 )
class User(AbstractUser):
    """用户模型类"""
    # 添加手机字段
    mobile = models.CharField(max_length=11, unique=True, verbose_name='手机号')
    # 增加邮箱是否验证的字段
    email_active = models.BooleanField(default=False, verbose_name='邮箱验证状态')

    class Meta:
        db_table = "tb_users"
        verbose_name = '用户'
        verbose_name_plural = verbose_name



















