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

from somaafrica.persons.views import HealthCheckAPIView
from somaafrica.persons.views import (
    SignupAPIView,
    LoginAPIView,
    LogoutJWTAPIView,
    TokenRefreshView,
    RequestPasswordResetAPIView,
    ResetPasswordAPIView
)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("signup", SignupAPIView.as_view(), name="signup"),
    path("login", LoginAPIView.as_view(), name="login"),
    path("logout", LogoutJWTAPIView.as_view(), name="logout_token"),
    path(
        "request_password_reset",
        RequestPasswordResetAPIView.as_view(),
        name="request_password_reset"
    ),
    path(
        "reset_password/<str:guid>/<str:token>",
        ResetPasswordAPIView.as_view(),
        name="reset_password"
    ),
    path("api/health", HealthCheckAPIView.as_view(), name="health_check"),
    # path(
    #     "social/<str:backend>/",
    #     SocialLoginAPIView.as_view(),
    #     name="social-login"
    # ),
    path("token", LoginAPIView.as_view(), name="token_obtain_pair"),
    path("token/refresh", TokenRefreshView.as_view(), name="token_refresh"),
    path("persons/", include("somaafrica.persons.urls")),
]
