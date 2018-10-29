from django.contrib.auth.models import AbstractUser
from django.db import models
from users import constants
from utils import tjws
from utils.models import BaseModel


# AbstractUser: django自带的用户模型类,提供了以下定义好的字段
# username(用户名), first_name, last_name, email, password, groups,
# user_permissions, is_staff(访问Admin 站点), is_active(账号是否激活),
# is_superuser, last_login, date_joined(创建的时间 )
# 用户信息模型类


class User(AbstractUser):
    """用户信息模型类"""
    # 添加手机字段
    mobile = models.CharField(max_length=11, unique=True, verbose_name='手机号')
    # 增加邮箱是否验证的字段
    email_active = models.BooleanField(default=False, verbose_name='邮箱验证状态')
    # 添加默认地址
    default_address = models.ForeignKey('Address', related_name='users', null=True, blank=True, on_delete=models.SET_NULL, verbose_name='默认地址')

    class Meta:
        db_table = "tb_users"
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def generate_verify_email_url(self):
        """生成验证邮箱的url"""
        data = {
            "user_id": self.id,
            "email": self.email
        }
        token = tjws.dumps(data, constants.VERIFY_EMAIL_TOKEN_EXPIRES)
        # 验证网址链接
        verify_url = 'http://www.meiduo.site:8080/success_verify_email.html?token=' + token

        return verify_url

    @staticmethod
    def check_verify_email_token(token):
        """检查验证邮件的token"""

        # 拿到token中的数据
        data_dict = tjws.loads(token, constants.VERIFY_EMAIL_TOKEN_EXPIRES)
        email = data_dict.get('email')
        user_id = data_dict.get('user_id')

        # 根据数据从数据库中查找对象
        try:
            user = User.objects.get(id=user_id, email=email)
        except User.DoesNotExist:
            # 没找到,返回None
            return None
        else:
            # 找到了,返回对象数据
            return user


# 用户地址模型类
class Address(BaseModel):
    """用户地址"""
    user = models.ForeignKey(User, verbose_name='用户', on_delete=models.CASCADE, related_name='addresses')
    title = models.CharField(verbose_name='地址名称', max_length=20)
    receiver = models.CharField(verbose_name='收货人', max_length=20)
    province = models.ForeignKey('areas.Area', verbose_name='省', on_delete=models.PROTECT, related_name='province_addresses')
    city = models.ForeignKey('areas.Area', verbose_name='市', on_delete=models.PROTECT, related_name='city_addresses')
    district = models.ForeignKey('areas.Area', verbose_name='区', on_delete=models.PROTECT, related_name='district_addresses')
    place = models.CharField(verbose_name='详细地址', max_length=50)
    mobile = models.CharField(verbose_name='手机号', max_length=11)
    tel = models.CharField(verbose_name='固定电话', max_length=20, null=True, blank=True, default='')
    email = models.CharField(verbose_name='电子邮箱地址', max_length=30, null=True, blank=True, default='')
    is_deleted = models.BooleanField(default=False, verbose_name='逻辑删除')

    class Meta:
        db_table = 'tb_address'
        verbose_name = '用户地址'
        verbose_name_plural = verbose_name
        ordering = ['-update_time']  # 更新时间的倒序排序









