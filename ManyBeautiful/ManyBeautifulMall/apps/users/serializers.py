from rest_framework import serializers
import re
from django_redis import get_redis_connection

from celery_tasks.email.tasks import send_verify_email
from utils import jwt_token
from .models import *


# 创建用户的序列化器
class CreateUserSerializer(serializers.Serializer):
    """
    创建用户的序列化器
    属性: id, username, password, password2,sms_code, mobile, allow

    """

    # 定义属性
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(
        min_length=5,
        max_length=20,
        error_messages={
            'min_length': '用户名为5-20个字符',
            'max_length': '用户名为5-20个字符'
        })
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        max_length=20,
        error_messages={
            'min_length': '密码为8-20个字符',
            'max_length': '密码为8-20个字符'
        })
    password2 = serializers.CharField(
        write_only=True,
        min_length=8,
        max_length=20,
        error_messages={
            'min_length': '密码为8-20个字符',
            'max_length': '密码为8-20个字符'
        })
    sms_code = serializers.CharField(write_only=True)
    mobile = serializers.CharField()
    allow = serializers.BooleanField(write_only=True)

    # 添加token字段
    token = serializers.CharField(label='登录状态token', read_only=True)

    # 验证
    def validate_username(self, value):
        """验证用户是否存在"""
        if User.objects.filter(username=value).count() > 0:
            raise serializers.ValidationError("当前用户以存在")
        return value

    def validate_mobile(self, value):
        """验证手机号格式"""
        if not re.match('^1[3-9]\d{9}$', value):
            raise serializers.ValidationError("手机号格式有误")
        """验证手机号是否重复"""
        count = User.objects.filter(mobile=value).count()
        if count > 0:
            raise serializers.ValidationError('手机号不存在')

        return value

    def validate_allow(self, value):
        """验证是否同意协议"""
        if not value:
            raise serializers.ValidationError("必须同意协议")
        return value

    def validate(self, attrs):

        # 验证短信验证码
        redis_cli = get_redis_connection("sms_code")
        # attrs表示请求报文中所有的属性与值，类型为字典
        key = 'sms_code_' + attrs.get('mobile')
        sms_code_redis = redis_cli.get(key)
        # 判断redis中是否还存有验证码
        if not sms_code_redis:
            raise serializers.ValidationError('验证码已经过期')
        redis_cli.delete(key)
        # 比对redis中存的验证码和用户输入的验证码是否匹配
        sms_code_redis = sms_code_redis.decode()
        sms_code_request = attrs.get("sms_code")
        if int(sms_code_redis) != int(sms_code_request):
            raise serializers.ValidationError('验证码错误')

        # 验证两次输入的密码正误
        pwd1 = attrs.get('password')
        pwd2 = attrs.get('password2')
        if pwd1 != pwd2:
            raise serializers.ValidationError('两次输入的密码不一致')

        return attrs

    # 新建数据
    def create(self, validated_data):  # validated_data 上方验证通过后,数据保存在这里
        """新建数据"""
        user = User()
        user.username = validated_data.get('username')
        user.mobile = validated_data.get('mobile')
        # user.password=validated_data.get('password')
        # 密码需要加密
        user.set_password(validated_data.get('password'))
        user.save()

        # 生成记录登录状态的token
        # jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        # jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        # payload = jwt_payload_handler(user)
        # token = jwt_encode_handler(payload)
        token = jwt_token.generate(user)
        user.token = token

        return user


# 用户中心的序列化器
class UserDetailSerializer(serializers.ModelSerializer):
    """用户中心的序列化器"""
    class Meta:
        model = User
        fields = ('id', 'username', 'mobile', 'email', 'email_active')


# 邮箱序列化器
class EmailSerializer(serializers.ModelSerializer):
    """邮箱序列化器"""

    class Meta:
        model = User
        fields = ("id", "email")
        extra_kwargs = {
            'email': {
                'required': True
            }
        }

    def update(self, instance, validated_data):  # instance为待修改的模型类对象

        instance.email = validated_data.get("email")
        email = validated_data["email"]
        instance.save()

        # 生成验证链接(模型类调用生成链接方法)
        verify_url = instance.generate_verify_email_url()
        # 使用celery_tasks中定义的发短信方法,使用工人发送短息
        send_verify_email.delay(email, verify_url)

        return instance


# 验证邮件序列化器
class EmailActiveSerializer(serializers.Serializer):
    """验证邮件"""
    token = serializers.CharField(max_length=2000)

    def validate(self, attrs):
        # 获取加密字符中
        token = attrs.get('token')
        # 解密
        data_dict = tjws.loads(token, constants.VERIFY_EMAIL_TOKEN_EXPIRES)
        # 判断是否过期
        if data_dict is None:
            raise serializers.ValidationError('激活链接已经过期')
        # 将获取到的user_id加入验证后的数据字典中
        attrs['user_id'] = data_dict.get('user_id')

        return attrs


# 用户地址序列化器
class UserAddressSerializer(serializers.ModelSerializer):
    """用户地址序列化器"""
    # 定义属性
    province_id = serializers.IntegerField(label='省ID', required=True)
    city_id = serializers.IntegerField(label='市ID', required=True)
    district_id = serializers.IntegerField(label='区ID', required=True)
    province = serializers.StringRelatedField(read_only=True)
    city = serializers.StringRelatedField(read_only=True)
    district = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Address
        exclude = ('user', 'is_deleted', 'create_time', 'update_time')

    # 验证
    def validate_mobile(self, value):
        """验证手机格式"""
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError('手机号格式错误')
        return value

    # 创建 重写create方法
    def create(self, validated_data):
        # 创建收货地址时,需要指定user属性,
        # 但这个值不是不是从客户端传过来的,而是获取当前登陆用户
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


# 地址标题序列化器
class AddressTitleSerializer(serializers.ModelSerializer):
    """地址标题"""

    class Meta:
        model = Address
        fields = ('title',)
