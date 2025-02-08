from rest_framework.routers import DefaultRouter

from .views import (
    UserViewSet,
    PermissionViewSet,
    GroupViewSet,
    PersonViewSet,
    AddressViewSet,
    PhoneViewSet
)


persons_router = DefaultRouter(trailing_slash=False)
persons_router.register(r'user', UserViewSet, 'user')
persons_router.register(r'permission', PermissionViewSet, 'permission')
persons_router.register(r'group', GroupViewSet, 'group')
persons_router.register(r'person', PersonViewSet, 'person')
persons_router.register(r'phone', PhoneViewSet, 'phone')
persons_router.register(r'address', AddressViewSet, 'address')

urlpatterns = persons_router.urls
