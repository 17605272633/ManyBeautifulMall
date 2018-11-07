import os

from alipay import AliPay
from django.conf import settings
from django.shortcuts import render
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from orders.models import OrderInfo


class PaymentView(APIView):
    """支付宝支付视图函数"""
    # 用户登陆验证
    permission_classes = [IsAuthenticated]

    def get(self,request, order_id):
        """
        获取支付链接
        请求方式： GET /orders/(?P<order_id>\d+)/payment/
        :param order_id: 订单编号
        :param request:
        :return: alipay_url	支付宝支付链接
        """

        # 获取订单信息并判断正误
        try:
            order = OrderInfo.objects.get(order_id=order_id,
                                          user=request.user,
                                          pay_method=2,  # OrderInfo.PAY_METHODS_ENUM["ALIPAY"]
                                          status=1)  # OrderInfo.ORDER_STATUS_ENUM["UNPAID"]
        except OrderInfo.DoesNotExist:
            return Response({'message': '订单信息有误'}, status=status.HTTP_400_BAD_REQUEST)

        # 构造支付宝连接地址
        alipay = AliPay(
            appid= settings.ALIPAY_APPID,
            app_notify_url=None,  # 默认回调路径
            app_private_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "keys/app_private_key.pem"),
            # 支付宝的公钥，验证支付宝回传消息使用，是自己从阿里获取的公钥
            alipay_public_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)),"keys/alipay_public_key.pem"),
            sign_type="RSA2",
            debug=settings.ALIPAY_DEBUG
        )

        # 调用支付宝的接口
        order_string = alipay.api_alipay_trade_page_pay(
            out_trade_no=order_id,
            total_amount=str(order.total_amount),
            subject="美多商城%s" % order_id,
            return_url="http://www.meiduo.site:8080/pay_success.html",
            notify_url="https://example.com/notify"  # 可选, 不填则使用默认notify url
        )

        # 电脑网站支付，需要跳转到https://openapi.alipay.com/gateway.do? + order_string
        # 拼接链接返回前端
        alipay_url = settings.ALIPAY_URL + "?" + order_string

        data = {
            'alipay_url': alipay_url
        }

        return Response(data)




