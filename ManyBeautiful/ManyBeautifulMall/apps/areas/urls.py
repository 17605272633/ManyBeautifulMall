from django.conf.urls import url
from . import views


urlpatterns = [

]

# 因为用的是视图集,所以使用router方法添加路由
from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register(r'areas', views.AreasViewSet, base_name='areas')
urlpatterns += router.urls
