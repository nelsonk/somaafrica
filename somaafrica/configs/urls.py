"""
URL configuration for somaafrica project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenBlacklistView
)

from somaafrica.persons.views import SignupAPIView, LoginAPIView, SocialLoginAPIView, LogoutJWTAPIView


urlpatterns = [
    path("admin/", admin.site.urls),
    path("signup", SignupAPIView.as_view(), name="signup"),
    path("login", LoginAPIView.as_view(), name="login"),
    path("social/<str:backend>/", SocialLoginAPIView.as_view(), name="social-login"),
    path("token", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh", TokenRefreshView.as_view(), name="token_refresh"),
    path('token/blacklist', TokenBlacklistView.as_view(), name='token_blacklist'),
    path("logout", LogoutJWTAPIView.as_view(), name="logout-token"),
    path("persons/", include("somaafrica.persons.urls")),
]
