from django.conf.urls import url
from . import views


urlpatterns = [
    url('^categories/(?P<category_id>\d+)/skus/$',views.SKUListView.as_view()),
]