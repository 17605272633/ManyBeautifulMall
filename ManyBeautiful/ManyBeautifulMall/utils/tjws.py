from itsdangerous import TimedJSONWebSignatureSerializer, BadData
from django.conf import settings


def dumps(data, expires):
    """加密"""
    # 创建对象
    serializer = TimedJSONWebSignatureSerializer(settings.SECRET_KEY, expires)
    # 加密
    token = serializer.dumps(data).decode()

    return token


def loads(data, expires):
    """解密"""
    # 创建对象
    serializer = TimedJSONWebSignatureSerializer(settings.SECRET_KEY, expires)
    # 解密
    try:
        data_dict = serializer.loads(data)
        return data_dict
    except BadData:
        # 抛异常的原因：超时
        return None


