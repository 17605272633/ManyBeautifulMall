import os
from alipay import AliPay
from django.conf import settings
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from orders.models import OrderInfo


# 支付宝支付视图类
from payments.models import Payment


class PaymentView(APIView):
    """支付宝支付视图类"""
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


# 支付结果视图类
class PaymentStatusView(APIView):
    """支付结果视图类"""

    def put(self, request):
        """

        :param request: request.query_params.dict()可以获得
                        out_trade_no 商户网站唯一订单号
                        trade_no 该交易在支付宝中的流水号
                        total_amount 订单总额
                        seller_id 收款支付宝账号的用户号
        :return: trade_id支付宝流水号

        """
        # 获取查询字符串数据
        data = request.query_params.dict()
        signature = data.pop('sign')

        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,  # 默认回调路径
            app_private_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "keys/app_private_key.pem"),
            alipay_public_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                "keys/alipay_public_key.pem"),
            sign_type="RSA2",
            debug=settings.ALIPAY_DEBUG
        )

        success = alipay.verify(data, signature)

        if success:
            # 订单编号
            order_id = data.get('out_trade_no')  # out_trade_no 商户网站唯一订单号
            # 支付宝支付流水号
            trade_id = data.get('trade_no')  # trade_no 该交易在支付宝中的流水号
            Payment.objects.create(
                order_id=order_id,
                trade_id=trade_id
            )
            order = OrderInfo.objects.filter(order_id=order_id, status=OrderInfo.ORDER_STATUS_ENUM['UNPAID']).update(
                status=OrderInfo.ORDER_STATUS_ENUM["UNCOMMENT"])
            return Response({'trade_id': trade_id})
        else:
            return Response({'message': '非法请求'}, status=status.HTTP_403_FORBIDDEN)




