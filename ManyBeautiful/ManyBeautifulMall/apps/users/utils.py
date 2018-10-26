import re

from django.contrib.auth.backends import ModelBackend

from users.models import User


def jwt_response_payload_handler(token, user=None, request=None):
    """
    自定义用户登陆时jwt认证成功返回数据

    需要在配置文件中JWT_AUTH指定token有效期和指定payload_handler为当前视函数
    """

    data = {
        'token': token,
        'user_id': user.id,
        'username': user.username
    }

    return data


class UsernameMobileAuthBackend(ModelBackend):
    """
    自定义认证后端代码,为用户名或手机号验证,而非用户名验证
    需要重写authenticate方法
    authenticate(self, request, username=None, password=None, **kwargs)
        request 本次认证的请求对象
        username 本次认证提供的用户账号, 可以是手机号
        password 本次认证提供的密码

    需要在配置文件中修改认证为自定义认证后端
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        # 判断username是用户名还是手机号
        try:
            if re.match('^1[3-9]\d{9}$', username):
                # 帐号为手机号格式
                user = User.objects.get(mobile=username)
            else:
                # 帐号为用户名
                user = User.objects.get(username=username)
        except User.DoesNotExist:
            return None

        # 判断密码
        if user is not None and user.check_password(password):
            # 返回user对象
            return user
        else:
            return None
