from rest_framework.routers import DefaultRouter

from .views import UserViewSet, PermissionViewSet, GroupViewSet


persons_router = DefaultRouter(trailing_slash=False)
persons_router.register(r'user', UserViewSet, 'user')
persons_router.register(r'permission', PermissionViewSet, 'permission')
persons_router.register(r'group', GroupViewSet, 'group')

urlpatterns = persons_router.urls
