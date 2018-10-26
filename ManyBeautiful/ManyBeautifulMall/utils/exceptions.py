import logging
from django.db import DatabaseError
from redis.exceptions import RedisError
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import exception_handler as drf_exception_handler

# 获取dev中定义的logger,用来记录日志
logger = logging.getLogger('django')


def exception_handler(exc, context):
    """
    异常处理
    :param exc: 异常
    :param context: 抛出异常的上下文
    :return: 异常信息
    """

    # 调用drf原生的异常处理方法
    response = drf_exception_handler(exc, context)

    if response is None:
        #
        view = context["view"]
        if isinstance(exc, DatabaseError) or isinstance(exc, RedisError):
            # 数据库异常(mysql和redis)
            logger.error('[%s] %s' % (view, exc))
            response = Response({'message': '服务器内部错误'}, status=status.HTTP_507_INSUFFICIENT_STORAGE)

    return response


