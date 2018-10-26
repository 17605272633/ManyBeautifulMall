from django_redis import get_redis_connection
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from celery_tasks.sms.tasks import send_sms_code
from utils.ytx_sdk.sendSMS import CCP
from . import constants
import random


# 实现短信验证码
class SMSCodeView(APIView):
    def get(self, request, mobile):
        """
        短信验证码
        路由: GET /sms_code/(?P<mobile>1[3-9]\d{9})/

        逻辑处理  检查是否在60s内有发送记录
                生成短信验证码
                保存短信验证码与发送记录
                发送短信

        :param request: 请求对象
        :param mobile: 手机号
        :return: 是否发送成功的响应
        """
        # 获取redis链接,用于后续查询获取短信验证码
        redis_cli = get_redis_connection('sms_code')

        # 查看redis中是否有短信验证码数据,有则60s内发送过短信
        sms_flag = redis_cli.get('sms_flag_' + mobile)
        if sms_flag:
            raise serializers.ValidationError('发送验证码太频繁')

        # 60s内没发送过短信,生成6为验证密码
        sms_code = random.randint(100000, 999999)

        # (优化)使用管道方式交互redis
        redis_pipeline = redis_cli.pipeline()
        # 保存60s验证码和60s发送标记
        redis_pipeline.setex('sms_code_' + mobile, constants.SMS_CODE_EXPIRES, sms_code)
        redis_pipeline.setex('sms_flag_' + mobile, constants.SMS_FLAG_EXPIRES, 1)
        # 执行方法时,提交上述命令,减少和redis交互次数,达到优化效果
        redis_pipeline.execute()

        # 发送短信
        # sms_code_expires = constants.SMS_CODE_EXPIRES / 60
        # CCP.sendTemplateSMS(mobile, sms_code, constants.SMS_CODE_EXPIRES / 60, 1)
        print(sms_code)
        send_sms_code.delay(mobile, sms_code, constants.SMS_CODE_EXPIRES / 60, 1)

        # 响应
        return Response({'message': 'ok'})
