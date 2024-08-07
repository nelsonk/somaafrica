from rest_framework.routers import DefaultRouter

from .views import UserViewSet

commons_router = DefaultRouter()
commons_router.register(r'user', UserViewSet, 'user')

urlpatterns = commons_router.urls
