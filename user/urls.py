from django.urls import path, re_path, include

# jwt authentication
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import views

urlpatterns = [
    re_path(r'^$', views.index, name='index'),
]
