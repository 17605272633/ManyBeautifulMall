# QQ登陆辅助工具类

from urllib.parse import urlencode, parse_qs
from urllib.request import urlopen
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadData
from django.conf import settings
import json
import logging


from oauth import constants
from oauth.exceptions import QQAPIError

logger = logging.getLogger('django')


class OAuthQQ(object):
    """QQ认证辅助工具类"""

    def __init__(self, client_id=None, client_secret=None, redirect_uri=None, state=None):
        self.client_id = client_id or settings.QQ_CLIENT_ID
        self.client_secret = client_secret or settings.QQ_CLIENT_SECRET
        self.redirect_uri = redirect_uri or settings.QQ_REDIRECT_URI
        self.state = state or settings.QQ_STATE  # 用于保存登录成功后的跳转页面路径

    def get_qq_login_url(self):
        """
        获取qq登陆的网址(获取Authorization Code)
        :return: url网址
        """
        params = {
            "response_type": 'code',  # 授权类型，此值固定为“code”
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'state': self.state,
            # 'scope': 'get_user_info',  # 请求用户授权时向用户显示的可进行授权的列表
        }

        url = 'https://graph.qq.com/oauth2.0/authorize?' + urlencode(params)
        return url

    def get_code(self, r_p):
        """
        获取code
        :return: code
        """
        code = r_p.get('code')

        return code

    def get_access_token(self, code):
        """
        获取access_token
        :param code: qq提供的code
        :return: access_token授权令牌
        """
        params = {
            'grant_type': 'authorization_code',  # 授权类型
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'redirect_uri': self.redirect_uri
        }

        # urlencode  将字典转成查询字符串
        url = 'https://graph.qq.com/oauth2.0/token?' + urlencode(params)
        # urlopen  发送http请求,默认发送get请求
        response = urlopen(url)
        # 返回response响应对象，可以通过read()读取响应体数据,为bytes类型
        response_data = response.read().decode()
        # parse_qs 将查询字符串格式数据转换为python的字典
        data = parse_qs(response_data)

        # 获取access_token
        access_token = data.get('access_token', None)

        if not access_token:
            logger.error('code=%s msg=%s' % (data.get('code'), data.get('msg')))
            raise QQAPIError

        # 因为获取的列表中是有三段
        # 分别为access_token(授权令牌), expires_in(该access token的有效期), refresh_token(获取新的Access_Token时需要提供的参数)
        return access_token[0]

    def get_open_id(self, access_token):
        """
        获取用户的openid
        :param access_token: qq提供的access_token授权令牌
        :return: open_id(唯一对应用户身份的标识)
        """

        url = 'https://graph.qq.com/oauth2.0/me?access_token=' + access_token
        response = urlopen(url)
        response_data = response.read().decode()
        try:
            # 检查返回数据的正误
            # 返回包: callback({"client_id": "YOUR_APPID", "openid": "YOUR_OPENID"});
            print(json.loads(response_data[10:-4]))
            data = json.loads(response_data[10:-4])
            print(data)
        except Exception:
            data = parse_qs(response_data)
            logger.error('code=%s msg=%s' % (data.get('code'), data.get('msg')))
            raise QQAPIError

        openid = data.get('openid', None)
        return openid

    @staticmethod
    def generate_save_user_token(openid):
        """
        生成保存用户数据的token
        :param openid: 用户的openid
        :return: token
        """
        serializer = Serializer(settings.SECRET_KEY, expires_in=constants.SAVE_QQ_USER_TOKEN_EXPIRES)
        data = {'openid': openid}
        # serializer.dumps(数据), 返回bytes类型
        token = serializer.dumps(data)
        return token.decode()

    @staticmethod
    def check_seve_user_token(token):
        """
        检查保存用户数据的token
        :param token: 保存用户数据的token
        :return: openid or None
        """

        # 检查token, 会抛出itsdangerous.BadData异常
        # Serializer(秘钥, 有效期秒)
        serializer = Serializer(settings.SECRET_KEY, expires_in=constants.SAVE_QQ_USER_TOKEN_EXPIRES)
        try:
            data = serializer.loads(token)
        except BadData:
            return None
        else:
            return data.get('openid')


# class OAuthWeiXin(object):
#     """微信认证辅助工具类"""
#
#     def __init__(self, client_id=None, client_secret=None, redirect_uri=None, state=None):
#         self.client_id = client_id or settings.WEIXIN_CLIENT_ID
#         self.client_secret = client_secret or settings.WEIXIN_CLIENT_SECRET
#         self.redirect_uri = redirect_uri or settings.WEIXIN_REDIRECT_URI
#         self.state = state or settings.WEIXIN_STATE  # 用于保存登录成功后的跳转页面路径
#
#     def get_weixin_login_url(self):
#         """
#         获取qq登陆的网址(获取Authorization Code)
#         :return: url网址
#         """
#         params = {
#             "response_type": 'code',  # 授权类型，此值固定为“code”
#             'client_id': self.client_id,
#             'redirect_uri': self.redirect_uri,
#             'state': self.state,
#             # 'scope': 'get_user_info',  # 请求用户授权时向用户显示的可进行授权的列表
#         }
#
#         url = 'https://open.weixin.qq.com/connect/qrconnect?' + urlencode(params)
#         return url