from django.conf.urls import url

from . import views

urlpatterns = [
    url('^categories/(?P<category_id>\d+)/skus/$', views.SKUListView.as_view()),
]


from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register('skus/search', views.SKUSearchViewSet, base_name='skus_search')
urlpatterns += router.urls
