import logging
# import pdb

from django.contrib.auth import authenticate, login
from django.contrib.auth.models import Permission
from django.db.models import Q
from django.shortcuts import get_object_or_404

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken
from social_core.backends.google import GoogleOAuth2
from social_core.backends.facebook import FacebookOAuth2
from social_core.exceptions import AuthException
from social_core.actions import do_complete

from .models import User, Group, Person
from .serializers import (
    UserSerializer,
    UserSignupSerializer,
    UserLoginSerializer,
    GroupSerializer,
    PermissionSerializer,
    PersonSerializer
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
            LOGGER.warning(str(e))
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
            LOGGER.warning(str(e))
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
                LOGGER.warning("Unsupported backend")
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
            LOGGER.warning(str(e))
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
            LOGGER.warning(str(e))
            # Handle any errors (e.g., invalid token)
            return Response(
                {"detail": f"Failed, {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )


class UserViewSet(ModelViewSet):
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
        "guid": ['exact'],
        'is_active': ['exact'],
        'is_superuser': ['exact']
    }
    search_fields = ['username', 'email', 'guid', 'created_at', 'updated_at']
    ordering_fields = ['username', 'email', 'guid', 'created_at', 'updated_at']
    ordering = 'created_at'

    perms_map = {
        'GET': ['add_user'],
        'OPTIONS': [],
        'HEAD': [],
        'POST': [],
        'PUT': ['modify_other_user'],
        'PATCH': [],
        'DELETE': ['delete_other_user'],
    }

    def get_queryset(self):
        user_id = self.request.user.guid
        admin_user = self.request.user.is_superuser

        if admin_user or self.request.user.has_perm("add_user"):
            return User.objects.all()

        return User.objects.filter(guid=user_id)

    @action(methods=['put'], detail=True)
    def change_password(self, request, pk=None):
        password1 = request.data.get("password1")
        password2 = request.data.get("password2")

        if not password1 or not password2:
            LOGGER.warning("Password numm")
            return Response(
                {"message": "Password null"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if password1 != password2:
            LOGGER.warning("Password mismatch")
            return Response(
                {"message": "Password mismatch"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = get_object_or_404(self.get_queryset(), pk=pk)
            user.change_password(password=password1)
            detail = (self.get_serializer(user)).data

            return Response(
                {"message": "User updated successfully", "detail": detail},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            LOGGER.warning(str(e))
            return Response(
                {"message": "Unsuccessful", "detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class PermissionViewSet(ReadOnlyModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    filterset_fields = {
        'codename': ['exact'],
        'content_type__id': ['exact'],
        'group__name': ['exact'],
        'id': ['exact'],
        'name': ['exact'],
        'user__guid': ['exact']
    }
    search_fields = [
        'codename',
        'content_type__id',
        'group__name',
        'id',
        'name',
        'user__guid'
    ]
    ordering_fields = [
        'codename',
        'content_type__id',
        'group__name',
        'id',
        'name',
        'user__guid'
    ]
    ordering = 'content_type'


class GroupViewSet(ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    filterset_fields = {
        'guid': ['exact'],
        'name': ['exact'],
        'permissions__codename': ['exact'],
        'user__guid': ['exact']
    }
    search_fields = ['guid', 'name', 'permissions__codename', 'user__guid']
    ordering_fields = ['guid', 'name', 'permissions__codename', 'user__guid']
    ordering = 'name'

    perms_map = {
        'GET': ['add_group'],
        'OPTIONS': [],
        'HEAD': [],
        'POST': [],
        'PUT': [],
        'PATCH': [],
        'DELETE': [],
    }

    def _handle_group_permissions(self, group, perms):
        try:
            permissions = Permission.objects.filter(codename__in=perms)
            group.permissions.clear()
            group.permissions.add(*permissions)
            group.save()
        except Exception as e:
            raise e

    @action(methods="post", detail=True)
    def update_permission(self, request, pk):
        perms = request.data.get("permissions")

        if not perms:
            return Response(
                data={"message": "List of permission codenames not provided"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            our_group = get_object_or_404(self.get_queryset(), pk=pk)
            self._handle_group_permissions(our_group, perms)

            our_group.refresh_from_db()
            our_data = self.get_serializer(our_group).data
            return Response(data=our_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                data={"message": "Unsuccessful", "detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(methods=["post"], detail=True)
    def add_user(self, request, pk=None):
        user = request.user
        user_guid = request.data.get("user_id")

        if not user.has_perm("add_user_to_group"):
            detail = "You don't have permissions to add user to group"
            LOGGER.warning(detail)
            return Response(
                data={"message": "Unsuccessful", "detail": detail},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            our_group = get_object_or_404(self.get_queryset(), pk=pk)
            our_group.add_user_to_group(user_guid)

            our_group.refresh_from_db()
            our_data = self.get_serializer(our_group).data

            return Response(
                data=our_data,
                status=status.HTTP_200_OK
            )

        except Exception as e:
            LOGGER.warning(str(e))
            return Response(
                data={"message": "Unsuccessful", "detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(methods=["post"], detail=True)
    def remove_user(self, request, pk=None):
        user = request.user
        user_id = request.data.get("user_id")

        if not user.is_superuser and not user.has_perm("remove_user_group"):
            detail = "You don't have permissions to add user"
            LOGGER.warning(detail)
            return Response(
                data={"message": "Unsuccessful", "detail": detail},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            our_group = get_object_or_404(self.get_queryset(), pk=pk)
            group_user = get_object_or_404(User, guid=user_id)
            group_user.groups.remove(our_group)

            detail = f" User {group_user} removed from group {our_group.name}"
            return Response(
                data={"message": "Successful", "detail": detail},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            LOGGER.warning(str(e))
            return Response(
                data={"message": "Unsuccessful", "detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class PersonViewSet(ModelViewSet):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    filterset_fields = {
        'guid': ['exact'],
        'name': ['exact'],
        'permissions__codename': ['exact'],
        'user__guid': ['exact']
    }
    search_fields = ['guid', 'name', 'permissions__codename', 'user__guid']
    ordering_fields = ['guid', 'name', 'permissions__codename', 'user__guid']
    ordering = 'name'

    perms_map = {
        'GET': ['add_group'],
        'OPTIONS': [],
        'HEAD': [],
        'POST': [],
        'PUT': [],
        'PATCH': [],
        'DELETE': [],
    }
