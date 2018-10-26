from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.settings import api_settings
from oauth.exceptions import QQAPIError
from oauth.models import OAuthQQUser
from oauth.serializers import OAuthQQUserSerializer
from oauth.utils import OAuthQQ


class QQAuthURLView(APIView):
    """获取用户登录的url"""

    def get(self, request):
        """
        请求方式: GET /oauth/qq/authorization/?next=xxx
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
        code = request.query_params.get('code')
        if not code:
            return Response({'message': '缺少code'}, status=status.HTTP_400_BAD_REQUEST)

        oauth = OAuthQQ()

        # 获取用户的openid
        try:
            access_token = oauth.get_access_token(code)
            openid = oauth.get_open_id(access_token)
        except QQAPIError:
            return Response({'message': 'QQ服务异常'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        # 通过openid判断用户是否存在
        try:
            qq_user = OAuthQQUser.objects.get(openid=openid)
        except OAuthQQUser.DoesNotExist:  # 不报错退出
            # 用户第一次使用QQ登录
            token = oauth.generate_save_user_token(openid)
            return Response({'access_token': token})

        else:
            # 找到用户,生成token
            user = qq_user.user
            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
            payload = jwt_payload_handler(user)
            token = jwt_encode_handler(payload)

            response = Response({
                'token': token,
                'user_id': user.id,
                'username': user.username
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
        serializer = OAuthQQUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        response = Response({
            'token': user.token,
            'user_id': user.id,
            'username': user.username
        })
        return response