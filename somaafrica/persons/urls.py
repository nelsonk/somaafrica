from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import UserViewSet


persons_router = DefaultRouter(trailing_slash=False)
persons_router.register(r'user', UserViewSet, 'user')

urlpatterns = persons_router.urls
