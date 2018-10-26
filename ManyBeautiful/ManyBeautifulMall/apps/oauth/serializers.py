from rest_framework import serializers
from users.models import User
from .models import OAuthQQUser
from .utils import OAuthQQ
from django_redis import get_redis_connection
from rest_framework_jwt.settings import api_settings


class OAuthQQUserSerializer(serializers.ModelSerializer):
    """
    保存QQ用户序列化器
    """
    # 定义新增属性
    sms_code = serializers.CharField(label='短信验证码', write_only=True)
    access_token = serializers.CharField(label='操作凭证', write_only=True)
    token = serializers.CharField(read_only=True)
    mobile = serializers.RegexField(label='手机号', regex=r'^1[3-9]\d{9}$')

    class Meta:
        model = User
        fields = ('mobile', 'password', 'sms_code', 'access_token', 'id', 'username', 'token')
        extra_kwargs = {
            'username': {
                'read_only': True
            },
            'password': {
                'write_only': True,
                'min_length': 8,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许8-20个字符的密码',
                    'max_length': '仅允许8-20个字符的密码',
                }
            },
            'password2': {
                'write_only': True,
                'min_length': 8,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许8-20个字符的密码',
                    'max_length': '仅允许8-20个字符的密码',
                }
            }
        }

        # 验证
        def validate(self, attrs):

            # 检查access_token
            access_token = attrs['access_token']
            openid = OAuthQQ.check_seve_user_token(access_token)
            if not openid:
                raise serializers.ValidationError('无效的access_token')
            attrs['openid'] = openid

            # 检查短信验证码
            mobile = attrs['mobile']
            sms_code = attrs['sms_code']
            # 获取redis中真正的密码(bytes类型)
            redis_cli = get_redis_connection('sms_code')
            real_sms_code = redis_cli.get('sms_code_%s' % mobile)
            if real_sms_code.decode() != sms_code:
                raise serializers.ValidationError('短信验证码错误')

            # 查询用户是否存在
            try:
                user = User.objects.get(mobile=mobile)
            except User.DoesNotExist:
                # 不存在,跳过此步奏
                pass
            else:
                # 判断密码
                password = attrs['password']
                if not user.check_password(password):
                    raise serializers.ValidationError('密码错误')
                attrs['user'] = user

            return attrs

        # 新建数据
        def create(self, validated_data):  # validated_data 上方验证通过后,数据保存在这里
            user = validated_data.get('user')
            openid = validated_data['openid']

            if not user:
                # 如果用户不存在，创建用户，绑定openid（创建了OAuthQQUser数据）
                mobile = validated_data['mobile']
                password = validated_data['password']
                user = User.objects.create_user(username=mobile, mobile=mobile, password=password)

            # 创建用户
            OAuthQQUser.objects.create(user=user, openid=openid)

            # 签发jwt token
            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
            payload = jwt_payload_handler(user)
            token = jwt_encode_handler(payload)

            user.token = token


