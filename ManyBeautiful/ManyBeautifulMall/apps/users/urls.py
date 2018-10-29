from django.conf.urls import url
from . import views
from rest_framework_jwt.views import obtain_jwt_token


urlpatterns = [
    # 验证用户名
    url(r'^usernames/(?P<username>\w{5,20})/count/$', views.UsernameCountView.as_view()),
    # 验证手机号
    url(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count/$', views.MobileCountView.as_view()),
    # 用户注册
    url(r'^users/$', views.UserCreateView.as_view()),
    # 用户登录
    url(r'^authorizations/$', obtain_jwt_token),
    # 详情页
    url(r'^user/$', views.UserDetailView.as_view()),
    # 用户邮箱设置
    url(r'^emails/$', views.EmailView.as_view()),
    # 用户邮箱验证
    url(r'^emails/verification/$', views.VerifyEmailView.as_view()),

]


from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register(r'addresses', views.AddressViewSet, base_name='addresses')
urlpatterns += router.urls