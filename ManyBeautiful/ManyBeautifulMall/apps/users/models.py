from django.contrib.auth.models import AbstractUser
from django.db import models
from users import constants
from utils import tjws


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
        print(email)
        print(user_id)

        # 根据数据从数据库中查找对象
        try:
            user = User.objects.get(id=user_id, email=email)
        except User.DoesNotExist:
            # 没找到,返回None
            return None
        else:
            # 找到了,返回对象数据
            return user












