import logging

from django.contrib.auth import authenticate, login, logout
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from .authentication_backends import AuthenticationError
from .models import User
from .serializer import UserSerializer


LOGGER = logging.getLogger(__name__)


class UserViewSet(ReadOnlyModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'username': ['icontains'],
        'email': ['exact'],
        "id": ['exact']
    }

    def get_queryset(self):
        user_id = self.request.user.id
        admin_user = self.request.user.is_staff

        if admin_user:
            return User.objects.all()

        return User.objects.filter(id=user_id)

    def get_permissions(self):
        if self.action in ['login', 'signup']:
            return [AllowAny()]

        return super().get_permissions()

    @csrf_exempt
    @action(methods=['post'], detail=False)
    def signup(self, request):
        username = request.data.get("username")
        password1 = request.data.get("password1")
        password2 = request.data.get("password2")
        email = request.data.get("email")
        core_fields = ["username", "password1", "password2", "email"]
        extra_fields = {}

        if password1 != password2:
            return Response(
                {"message": "Passwords don't match"},
                status=status.HTTP_406_NOT_ACCEPTABLE
            )

        for key, value in request.data.items():
            if key not in core_fields:
                extra_fields[key] = value

        try:
            user = User.objects.create_user(
                username=username,
                password=password1,
                email=email,
                **extra_fields
            )

            return Response(
                {
                    "message": "User created successfully",
                    "user_id": user.id,
                    "username": user.username
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"message": str(e)},
                status=status.HTTP_406_NOT_ACCEPTABLE
            )

    @csrf_exempt
    @action(methods=['post'], detail=False)
    def login(self, request):
        """
        Return a list of all users.
        """
        username = request.data.get("username")
        password = request.data.get("password")
        LOGGER.info(f"Username {username}, password {password}")

        try:
            user = authenticate(request, username=username, password=password)
            login(request, user)

            user_response = {
                "user_id": user.id,
                "email": user.email,
                "username": user.username
            }
            return Response({"message": "OK", "detail": user_response})

        except (AuthenticationError, User.DoesNotExist) as e:
            # pdb.set_trace()
            LOGGER.error(e)
            return Response(
                {
                    "message": str(e),
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

    @action(methods=['post'], detail=False)
    def logout(self, request):
        logout(request)
        return Response({"message": "User logged out successfully"})

    @action(methods=['put'], detail=True)
    def change_password(self, request, pk=None):
        password1 = request.data.get("password1")
        password2 = request.data.get("password2")

        if not password1 or not password2:
            return Response(
                {"message": "Password null"},
                status=status.HTTP_204_NO_CONTENT
            )

        if password1 != password2:
            return Response(
                {"message": "Password mismatch"},
                status=status.HTTP_406_NOT_ACCEPTABLE
            )

        try:
            user = get_object_or_404(self.get_queryset(), pk=pk)
            user.set_password(request.data.get("password"))
            user.save()
            detail = (self.get_serializer(user)).data

            return Response(
                {"message": "User updated successfully", "detail": detail},
                status=status.HTTP_202_ACCEPTED
            )

        except Exception as e:
            return Response({"message": "Unsuccessful", "detail": str(e)})

    @action(methods=['delete'], detail=True)
    def delete(self, request, pk=None):
        try:
            count, _ = self.get_queryset().filter(pk=pk).delete()
            return Response(
                {"message": f" {count} User deleted successfully"}
            )

        except Exception as e:
            return Response({"message": "Unsuccessful", "detail": str(e)})

    @action(methods=['get'], detail=False)
    def list_active_users(self, request):
        # Filtering the queryset
        data = self.get_queryset().filter(is_active=True)
        queryset = self.filter_queryset(data)

        # Paginating the queryset manually
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        # Fallback if pagination is not required
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
