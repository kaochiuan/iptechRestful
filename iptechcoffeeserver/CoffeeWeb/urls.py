"""CoffeeWeb URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from rest_framework import routers
from rest_framework.authtoken import views
from rest_framework_jwt.views import ObtainJSONWebToken, RefreshJSONWebToken
from CoffeeWeb.RestAPI.views import UserViewSet, GroupViewSet
from CoffeeWeb.RestAPI.views import MenuViewSet, AuthView
from CoffeeWeb.RestAPI.views import ConsumeViewSet, StoreViewSet
from CoffeeWeb.RestAPI.views import ProfileViewSet, DeviceInfoViewSet
from django.contrib import admin

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'groups', GroupViewSet)
router.register(r'menus', MenuViewSet)
router.register(r'consumeRecords', ConsumeViewSet)
router.register(r'stores', StoreViewSet)
router.register(r'profiles', ProfileViewSet)
router.register(r'devices', DeviceInfoViewSet)

urlpatterns = [url(r'^admin/', admin.site.urls),
               url(r'^', include(router.urls)),
               url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
               url(r'^auth/', AuthView.as_view(), name='auth-view'),
               url(r'^api-token-auth/', ObtainJSONWebToken.as_view()),
               url(r'^api-token-refresh/', RefreshJSONWebToken.as_view()),
	       url(r'^app-token-auth/', views.obtain_auth_token),
              ]
