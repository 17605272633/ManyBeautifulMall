from rest_framework import status
from rest_framework.generics import *
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from users.models import User
from users.serializers import *


# 统计该用户名数量的类视图
class UsernameCountView(APIView):
    """统计该用户名数量的类视图"""

    def get(self, request, username):
        """
        统计该用户名数量
        路由: GET usernames/(?P<username>\w{5,20})/count/

        :param username: 用户名
        :return: {'username':'xxxxx', 'count': 'x'}  username用户名,count数量
        """

        # 获取该用户名用户数量
        count = User.objects.filter(username=username).count()

        # 组织响应数据
        data = {
            'username': username,
            'count': count
        }

        # 响应json数据
        return Response(data)


# 统计该用户手机号数量的类视图
class MobileCountView(APIView):
    """统计该用户手机号数量的类视图"""

    def get(self, request, mobile):
        """
        统计该用户手机号数量
        路由: GET mobiles/(?P<mobile>1[3-9]\d{9})/count/

        :param mobile: 用户手机号
        :return: {'mobile': 'xxxxxxxxxxx', 'count': 'x'}  mobile手机号,count数量
        """

        count = User.objects.filter(mobile=mobile).count()

        data = {
            'mobile': mobile,
            'count': count
        }

        return Response(data)


# 用户注册类视图
class UserCreateView(CreateAPIView):
    """
    用户注册类视图
    CreateAPIView中有封装相对应的请求方式,创建新用户等代码,此视图函数中只需要定义serializer对象
    路由: POST /users/

    不需要查询集,只做创建不做查询
    serializers.py中定义了CreateUserSerializer.此处只需要调用序列化器
    """

    serializer_class = CreateUserSerializer


# 用户详情页类视图
class UserDetailView(RetrieveAPIView):
    """用户详情页类视图"""
    # queryset = User.objects.all()
    serializer_class = UserDetailSerializer
    # 用户认证
    permission_classes = [IsAuthenticated]

    # 视图中封装好的代码,是根据主键查询得到对象
    # 根据登陆的用户,显示个人信息
    # get_object默认根据pk查询,重写get_object
    def get_object(self):  # self是序列化器对象,request.user代表登录用户
        return self.request.user


# 保存用户邮箱
class EmailView(UpdateAPIView):
    """保存用户邮箱"""

    serializer_class = EmailSerializer
    # 必须是登陆过后的用户
    permission_classes = [IsAuthenticated]

    def get_object(self):  # 返回当前登陆的用户数据
        return self.request.user


# 邮箱验证
class VerifyEmailView(APIView):
    """邮箱认证"""

    def get(self, request):
        """
        请求方式: GET  /emails/verification/?token=
        :param request: 可用于获取查询字符串的请求
        :return: {'message': 'OK'}
        """
        # 获取token
        token = request.query_params.get('token')
        if not token:
            return Response({'message': '缺少token'}, status=status.HTTP_400_BAD_REQUEST)

        # 验证token
        user = User.check_verify_email_token(token)
        if user is None:
            return Response({'message': '链接信息无效'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            user.email_active = True
            user.save()

            return Response({'message': 'OK'})













