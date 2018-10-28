from rest_framework import serializers

from . import constants
from users.models import User
from utils import tjws
from .models import OAuthQQUser
from .utils import OAuthQQ
from django_redis import get_redis_connection
from rest_framework_jwt.settings import api_settings


class OAuthQQUserSerializer(serializers.Serializer):
    """
    保存QQ用户序列化器
    """
    # 定义新增属性
    sms_code = serializers.CharField(label='短信验证码', write_only=True)
    access_token = serializers.CharField(label='操作凭证', write_only=True)
    # token = serializers.CharField(read_only=True)
    mobile = serializers.RegexField(label='手机号', regex=r'^1[3-9]\d{9}$')
    password = serializers.CharField(write_only=True, min_length=8, max_length=20, error_messages={
                    'min_length': '仅允许8-20个字符的密码',
                    'max_length': '仅允许8-20个字符的密码',
                })

    # class Meta:
    #     model = User
    #     fields = ('mobile', 'password', 'sms_code', 'access_token', 'id', 'username', 'token')
    #     extra_kwargs = {
    #         'username': {
    #             'read_only': True
    #         },
    #         'password': {
    #             'write_only': True,
    #             'min_length': 8,
    #             'max_length': 20,
    #             'error_messages': {
    #                 'min_length': '仅允许8-20个字符的密码',
    #                 'max_length': '仅允许8-20个字符的密码',
    #             }
    #         }
    #
    #     }

    # 验证
    def validate(self, attrs):

        # 检查短信验证码
        mobile = attrs['mobile']
        sms_code = attrs['sms_code']
        # 获取redis中真正的密码(bytes类型)
        redis_cli = get_redis_connection('sms_code')
        real_sms_code = redis_cli.get('sms_code_%s' % mobile)
        if real_sms_code.decode() != sms_code:
            raise serializers.ValidationError('短信验证码错误')

        # 检查access_token
        access_token = attrs['access_token']
        data_dict = tjws.loads(access_token, constants.SAVE_QQ_USER_TOKEN_EXPIRES)
        if not data_dict:
            raise serializers.ValidationError('无效的access_token')
        openid = data_dict.get("openid")
        # 将openid加入字典
        attrs['openid'] = openid

        return attrs

    # 新建数据
    def create(self, validated_data):  # validated_data 上方验证通过后,数据保存在这里
        mobile = validated_data.get('mobile')
        openid = validated_data['openid']
        password = validated_data['password']

        # 查询用户是否存在
        try:
            user = User.objects.get(mobile=mobile)
        except:
            # 如果用户不存在，创建用户，绑定openid（创建了OAuthQQUser数据）
            user = User()
            user.mobile = mobile
            user.username = mobile
            user.set_password(password)
            user.save()
        else:
            # 判断用户密码是否正确
            if not user.check_password(password):
                raise serializers.ValidationError('密码错误')

        # 用户存在,创建QQUser用户对象
        qquser = OAuthQQUser()
        qquser.openid = openid
        qquser.user = user
        qquser.save()

        return qquser


