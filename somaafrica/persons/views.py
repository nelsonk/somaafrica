import logging
# import pdb

from django.contrib.auth import authenticate, login
from django.db.models import Q
from django.shortcuts import get_object_or_404

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken
from social_core.backends.google import GoogleOAuth2
from social_core.backends.facebook import FacebookOAuth2
from social_core.exceptions import AuthException
from social_core.actions import do_complete

from .models import User
from .serializers import (
    UserSerializer,
    UserSignupSerializer,
    UserLoginSerializer
)


LOGGER = logging.getLogger(__name__)


class SignupAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            serializer = UserSignupSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            password = serializer.validated_data.pop('password1')
            serializer.validated_data['password'] = password
            serializer.validated_data.pop('password2')

            user = User.objects.create_user(**serializer.validated_data)
            user_serializer = UserSerializer(user)

            return Response(
                {
                    "message": "User created Successfully",
                    "user": user_serializer.data
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"message": str(e)},
                status=status.HTTP_406_NOT_ACCEPTABLE
            )


class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        login_serializer = UserLoginSerializer(data=request.data)
        login_serializer.is_valid(raise_exception=True)

        try:
            # pdb.set_trace
            user = authenticate(request, **login_serializer._validated_data)
            login(request, user)

            user_serializer = UserSerializer(user)
            return Response(
                {"message": "Successful", "detail": user_serializer.data}
            )

        except Exception as e:
            return Response(
                {"message": "Authentication failed", "detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class SocialLoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, backend):
        try:
            # Get the backend (e.g., Google, Facebook)
            if backend == 'google':
                backend_class = GoogleOAuth2()
            elif backend == 'facebook':
                backend_class = FacebookOAuth2()
            else:
                return Response(
                    {'error': 'Unsupported backend'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Authenticate user via social backend
            user = do_complete(
                backend_class,
                request,
                request.data.get('access_token')
            )

            if user and not User.objects.filter(
                Q(email=user.email) | Q(username=user.username)
            ).exists():
                # Create a new user if necessary
                user = User.objects.create_user(
                    username=user.username,
                    email=user.email
                )
                user.set_unusable_password()
                user.save()

            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })

        except AuthException as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class LogoutJWTAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Get the refresh token from the request data
            refresh_token = request.data["refresh"]
            # Create a RefreshToken object from the token string
            token = RefreshToken(refresh_token)
            # Blacklist the refresh token
            token.blacklist()

            return Response(
                {"detail": "Token blacklisted, Successfully logged out."},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            # Handle any errors (e.g., invalid token)
            return Response(
                {"detail": f"Failed, {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )


class UserViewSet(ReadOnlyModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    filterset_fields = {
        'username': ['exact'],
        'email': ['exact'],
        "id": ['exact']
    }
    search_fields = ['username', 'email', 'id', 'created_at', 'updated_at']
    ordering_fields = ['username', 'email', 'id', 'created_at', 'updated_at']
    ordering = 'created_at'

    def get_queryset(self):
        user_id = self.request.user.id
        admin_user = self.request.user.is_staff

        if admin_user:
            return User.objects.all()

        return User.objects.filter(id=user_id)

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
            user.set_password(password1)
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
