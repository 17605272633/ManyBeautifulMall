from django.shortcuts import render
from rest_framework.generics import *
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from users import serializers
from users.models import User
from users.serializers import UserDetailSerializer


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


class UserCreateView(CreateAPIView):
    """
    用户注册类视图
    CreateAPIView中有封装相对应的请求方式,创建新用户等代码,此视图函数中只需要定义serializer对象
    路由: POST /users/

    不需要查询集,只做创建不做查询
    serializers.py中定义了CreateUserSerializer.此处只需要调用序列化器
    """

    serializer_class = serializers.CreateUserSerializer


class UserDetailView(RetrieveAPIView):
    """用户详情页类视图"""
    serializer_class = UserDetailSerializer
    # 用户认证
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user












