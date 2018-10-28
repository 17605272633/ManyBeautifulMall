from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from oauth.exceptions import QQAPIError
from oauth.models import OAuthQQUser
from oauth.serializers import OAuthQQUserSerializer
from oauth.utils import *
from utils import tjws, jwt_token


class QQAuthURLView(APIView):
    """获取QQ用户登录的url"""

    def get(self, request):
        """
        点击qq登陆,绑定的路由为/qq/authorization/?next=/, 路由绑定了此视图函数,视图函数返回json形式的,带参数的地址,客户端跳转此地址

        请求地址: GET
        提供用于qq登录的url
        :param request: 包含: next 用户QQ登录成功后进入美多商城的哪个网址
        :return: {
                    "login_url": 'https://graph.qq.com/oauth2.0/authorize?' + urlencode(params)
                }
        """

        next = request.query_params.get('next')
        oauth = OAuthQQ(state=next)
        login_url = oauth.get_qq_login_url()

        return Response({'login_url': login_url})


class QQAuthUserView(APIView):
    """QQ登陆的用户"""

    def get(self, request):
        """
        获取qq登陆的用户数据
        :param request: 包含数据的请求
        :return: response响应
        """
        # 获取QQ返回的授权凭证
        # code = oauth.get_code(request.query_params)

        code = request.query_params.get('code')
        if not code:
            return Response({'message': '缺少code'}, status=status.HTTP_400_BAD_REQUEST)

        oauth = OAuthQQ()

        # 获取用户的access_token, openid
        try:
            access_token = oauth.get_access_token(code)
            openid = oauth.get_open_id(access_token)
        except QQAPIError:
            return Response({'message': 'QQ服务异常'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        # 通过openid判断用户是否存在
        try:
            qquser = OAuthQQUser.objects.get(openid=openid)
        except OAuthQQUser.DoesNotExist:  # 不报错退出
            # 如果不存在，则通知客户端转到绑定页面
            # 用户第一次使用QQ登录
            # 将openid加密存入token中
            token = tjws.dumps({'openid': openid}, constants.SAVE_QQ_USER_TOKEN_EXPIRES)
            return Response({
                'access_token': token  # 由序列化器接收,用于解密后获取openid
            })

        else:
            # 找到用户,生成token
            user = qquser.user
            token = jwt_token.generate(user)

            response = Response({
                'token': token,
                'user_id': qquser.id,
                'username': qquser.user.username
            })

            return response

    def post(self, request):
        """
        绑用户接口
        :param request: mobile手机号,password密码,sms_code短信验证码,access_token凭据
                        都在request.data中,传入了序列化器
        :return: {
                    'token': user.token,
                    'user_id': user.id,
                    'username': user.username
                }
        """
        # 接收数据
        serializer = OAuthQQUserSerializer(data=request.data)
        # 验证
        if not serializer.is_valid():
            return Response({'message': serializer.errors})
        # 保存
        qquser = serializer.save()
        # 生成token
        user = qquser.user
        token = jwt_token.generate(user)
        # 响应
        response = Response({
            'token': token,
            'user_id': qquser.id,
            'username': qquser.user.username
        })
        return response


# class WeiXinAuthURLView(APIView):
#     """获取微信用户登录的url"""
#
#     def get(self, request):
#         """
#         点击微信登陆,绑定的路由为/微信/authorization/?next=/, 路由绑定了此视图函数,视图函数返回json形式的,带参数的地址,客户端跳转此地址
#
#         请求地址: GET
#         提供用于qq登录的url
#         :param request: 包含: next 用户QQ登录成功后进入美多商城的哪个网址
#         :return: {
#                     "login_url": 'https://open.weixin.qq.com/connect/qrconnect?' + urlencode(params)
#                 }
#         """
#
#         next = request.query_params.get('next')
#         oauth = OAuthWeiXin(state=next)
#         login_url = oauth.get_weixin_login_url()
#
#         return Response({'login_url': login_url})
#
