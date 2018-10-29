from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.mixins import CreateModelMixin, UpdateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from users.models import User
from users.serializers import CreateUserSerializer, UserDetailSerializer, EmailSerializer, UserAddressSerializer, \
    AddressTitleSerializer, constants, EmailActiveSerializer

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
        # # 获取token
        # token = request.query_params.get('token')
        # if not token:
        #     return Response({'message': '缺少token'}, status=status.HTTP_400_BAD_REQUEST)
        #
        # # 验证token
        # user = User.check_verify_email_token(token)
        # if user is None:
        #     return Response({'message': '链接信息无效'}, status=status.HTTP_400_BAD_REQUEST)
        # else:
        #     user.email_active = True
        #     user.save()

        # 接收数据并验证
        serializer = EmailActiveSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors)

        # 查询当前用户，并修改属性
        user = User.objects.get(pk=serializer.validated_data.get('user_id'))
        user.email_active = True
        user.save()

        # 响应
        return Response({'message': 'OK'})


# 用户地址 Z S G C
class AddressViewSet(CreateModelMixin, UpdateModelMixin, GenericViewSet):
    """
    用户地址的新增于修改
    POST /addresses/ 新建  -> create
    PUT /addresses/<pk>/ 修改  -> update
    GET /addresses/  查询  -> list
    DELETE /addresses/<pk>/  删除 -> destroy
    PUT /addresses/<pk>/status/ 设置默认 -> status
    PUT /addresses/<pk>/title/  设置标题 -> title
    """

    serializer_class = UserAddressSerializer
    permission_classes = [IsAuthenticated]

    # 重写获取查询集
    def get_queryset(self):
        # 获取当前用户所有没被删除的地址
        return self.request.user.addresses.filter(is_deleted=False)

    def list(self, request, *args, **kwargs):  # 等同于 GET 的查询所有
        """
        用户地址列表数据
        访问路径: GET /addresses/
        :return:
        """
        addr_queryset = self.get_queryset()
        addr_serializer = self.get_serializer(addr_queryset, many=True)  # 因为是县市所有,所以要many = True
        user = self.request.user
        return Response({
            'user_id': user.id,
            'default_address_id': user.default_address_id,
            'limit': constants.USER_ADDRESS_COUNTS_LIMIT,
            'addresses': addr_serializer.data,
        })

    def create(self, request, *args, **kwargs):  # 等同于 POST 的创建
        """
        保存用户地址数据
        访问路径: POST /addresses/
        :return:
        """
        # 因为设置了地址上限，所以判断
        count = request.user.addresses.count()
        if count >= constants.USER_ADDRESS_COUNTS_LIMIT:
            return Response({'message': '保存地址数据已达到上限'}, status=status.HTTP_400_BAD_REQUEST)

        return super().create(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):  # 等同于 DELETE 的删除
        """
        删除用户地址数据
        :return:
        """
        # 获取用户地址数据
        user_address = self.get_object()

        # 逻辑删除
        user_address.is_deleted = True
        user_address.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['put'], detail=True)
    def status(self, request, pk=None):
        """
        设置默认地址
        访问路径: PUT /addresses/pk/status/
        :param pk: 主键
        :return: {'message': 'OK'}
        """
        # 获取当前地址数据
        address = self.get_object()
        # 将默认地址设置为当前地址
        request.user.default_address = address
        request.user.save()

        return Response({'message': 'OK'}, status=status.HTTP_200_OK)

    @action(methods=['put'], detail=True)
    def title(self, request, pk=None):
        """
        修改标题
        访问路径: PUT /addresses/pk/title/
        :param pk: 主键
        :return:
        """
        # 获取当前地址数据
        address = self.get_object()
        addr_serializer = AddressTitleSerializer(instance=address, data=request.data)
        if addr_serializer.is_valid() is False:
            return Response({'message': addr_serializer.errors})
        addr_serializer.save()

        return Response(addr_serializer.data)




