import logging
# import pdb

from datetime import datetime

from django.contrib.auth import authenticate, login
from django.contrib.auth.models import Permission
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
# from django.db.models import Q
from django.shortcuts import get_object_or_404

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, filters
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
# from social_core.backends.google import GoogleOAuth2
# from social_core.backends.facebook import FacebookOAuth2
# from social_core.exceptions import AuthException
# from social_core.actions import do_complete

from somaafrica.commons.validator import (
    validate_email_return_filters,
    validate_email_address
)
from somaafrica.configs.settings import FRONTEND_URL

from .models import User, Group, Person, Phone, Address
from .serializers import (
    UserSerializer,
    UserSignupSerializer,
    UserLoginSerializer,
    LogoutJWTAPIViewSerializer,
    ChangePasswordSerializer,
    GroupSerializer,
    PermissionSerializer,
    PersonSerializer,
    AddRemovePermissionsSerializer,
    AddRemoveUserSerializer,
    PhoneSerializer,
    RemovePhoneSerializer,
    RemoveAddressSerializer,
    ResetPasswordSerializer,
    RequestPasswordResetSerializer,
    AddressSerializer
)


LOGGER = logging.getLogger(__name__)


class HealthCheckAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response(
            {"status": "healthy", "time": datetime.now()},
            status=200
        )


class RequestPasswordResetAPIView(APIView):
    permission_classes = [AllowAny]

    def patch(self, request):
        password_serializer = RequestPasswordResetSerializer(data=request.data)
        password_serializer.is_valid(raise_exception=True)

        try:
            email_validated = validate_email_address(
                password_serializer.validated_data["email"]
            )

            if email_validated:
                user = get_object_or_404(
                    User,
                    **password_serializer.validated_data
                )

                token = default_token_generator.make_token(user)
                guid = user.guid

                # Construct reset link
                reset_link = f"{FRONTEND_URL}/password_reset/{guid}/{token}"

                # Send email
                send_mail(
                    "Password Reset Request",
                    f"Click the link to reset your password: {reset_link}",
                    "sales@somaafrica.com",
                    [user.email],
                    fail_silently=False,
                )

                detail = "Link to reset password has been sent to your email"
                return Response(
                    {
                        "message": "User found successfully",
                        "detail": detail,
                        "token": token
                    },
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {"message": "Unsuccessful", "detail": "Invalid email"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        except Exception as e:
            LOGGER.exception(str(e))
            return Response(
                {"message": "Unsuccessful", "detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class ResetPasswordAPIView(APIView):
    permission_classes = [AllowAny]

    def patch(self, request, guid, token):
        password_serializer = ResetPasswordSerializer(data=request.data)
        password_serializer.is_valid(raise_exception=True)

        try:

            user = get_object_or_404(User, pk=guid)

            if not default_token_generator.check_token(user, token):
                return Response(
                    {
                        "message": "Unsuccessful",
                        "detail": "Invalid or expired token."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            new_password = password_serializer.validated_data["password1"]
            user.set_password(new_password)
            user.save()

            return Response(
                    {
                        "message": "Successful",
                        "detail": "Password rest successfully"
                    },
                    status=status.HTTP_200_OK
                )

        except Exception as e:
            LOGGER.exception(str(e))
            return Response(
                {"message": "Unsuccessful", "detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


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
                    "detail": user_serializer.data
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            LOGGER.exception(str(e))
            return Response(
                {
                    "message": "Signup failed",
                    "detail": str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        login_serializer = UserLoginSerializer(data=request.data)
        login_serializer.is_valid(raise_exception=True)
        username = login_serializer._validated_data['username']

        try:
            # pdb.set_trace
            filters = validate_email_return_filters(username)
            get_object_or_404(
                User,
                **filters
            )

            user = authenticate(request, **login_serializer._validated_data)
            login(request, user)

            user_serializer = UserSerializer(user)

            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)

            return Response(
                {
                    "message": "Successful",
                    "detail": user_serializer.data,
                    "refresh": str(refresh),
                    "access": str(refresh.access_token)
                }
            )

        except Exception as e:
            LOGGER.exception(e)
            return Response(
                {"message": "Authentication failed", "detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class TokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        try:
            # Use the parent class to handle the refresh token process
            return super().post(request, *args, **kwargs)
        except (TokenError, InvalidToken) as e:
            # Handle token-related errors
            return Response(
                {
                    "detail": "Invalid or expired token. Please log in again.",
                    "error": str(e)
                },
                status=status.HTTP_401_UNAUTHORIZED
            )
        except Exception as e:
            # Handle any other errors that may occur
            return Response(
                {
                    "detail": "An error occurred during token refresh.",
                    "error": str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )


# class SocialLoginAPIView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request, backend):
#         try:
#             # Get the backend (e.g., Google, Facebook)
#             if backend == 'google':
#                 backend_class = GoogleOAuth2()
#             elif backend == 'facebook':
#                 backend_class = FacebookOAuth2()
#             else:
#                 LOGGER.warning("Unsupported backend")
#                 return Response(
#                     {'message': 'Failed', 'detail': 'Unsupported backend'},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )

#             # Authenticate user via social backend
#             user = do_complete(
#                 backend_class,
#                 request,
#                 request.data.get('access_token')
#             )

#             if user and not User.objects.filter(
#                 Q(email=user.email) | Q(username=user.username)
#             ).exists():
#                 # Create a new user if necessary
#                 user = User.objects.create_user(
#                     username=user.username,
#                     email=user.email
#                 )
#                 user.set_unusable_password()
#                 user.save()

#             # Generate JWT tokens
#             refresh = RefreshToken.for_user(user)
#             return Response({
#                 'refresh': str(refresh),
#                 'access': str(refresh.access_token),
#             })

#         except AuthException as e:
#             LOGGER.exception(str(e))
#             return Response(
#                 {'message': 'Failed', 'detail': str(e)},
#                 status=status.HTTP_400_BAD_REQUEST
#             )


class LogoutJWTAPIView(APIView):
    _ignore_model_permissions = True

    def post(self, request):
        logout_serializer = LogoutJWTAPIViewSerializer(data=request.data)
        logout_serializer.is_valid(raise_exception=True)

        try:
            # Get the refresh token from the request data
            refresh_token = logout_serializer.validated_data["refresh"]
            # Create a RefreshToken object from the token string
            token = RefreshToken(refresh_token)
            # Blacklist the refresh token
            token.blacklist()

            return Response(
                {"detail": "Token blacklisted, Successfully logged out."},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            LOGGER.exception(str(e))
            # Handle any errors (e.g., invalid token)
            return Response(
                {"message": "Failed", "detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class UserViewSet(ModelViewSet):
    serializer_class = UserSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    filterset_fields = {
        'username': ['exact'],
        'email': ['exact'],
        "guid": ['exact'],
        "groups__name": ['exact'],
        'is_active': ['exact'],
        'is_superuser': ['exact']
    }
    search_fields = [
        'username',
        'email',
        'guid',
        'groups__name',
        'created_at',
        'updated_at'
    ]
    ordering_fields = [
        'username',
        'email',
        'guid',
        'groups__name',
        'created_at',
        'updated_at'
    ]
    ordering = 'created_at'

    perms_map = {
        'GET': [],
        'POST': [],
        'PUT': [],
        'PATCH': [],
        'DELETE': [],
    }

    def get_queryset(self):
        user_guid = self.request.user.guid
        admin_user = self.request.user.is_superuser

        if admin_user or self.request.user.has_perm("modify_other_user"):
            return User.objects.all()

        return User.objects.filter(guid=user_guid)

    @action(methods=['patch'], detail=True)
    def change_password(self, request, pk=None):
        password_serializer = ChangePasswordSerializer(data=request.data)
        password_serializer.is_valid(raise_exception=True)

        try:
            filters = validate_email_return_filters(
                password_serializer.validated_data["username"]
            )
            get_object_or_404(
                User,
                **filters
            )

            authenticate(
                request,
                username=password_serializer.validated_data["username"],
                password=password_serializer.validated_data["password"]
            )

            user = get_object_or_404(self.get_queryset(), pk=pk)
            user.change_password(
                password=password_serializer.validated_data["password1"]
            )
            detail = (self.get_serializer(user)).data

            return Response(
                {"message": "User updated successfully", "detail": detail},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            LOGGER.exception(str(e))
            return Response(
                {"message": "Unsuccessful", "detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class PermissionViewSet(ReadOnlyModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
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
        'name': ['exact']
    }
    search_fields = [
        'codename',
        'content_type__id',
        'group__name',
        'id',
        'name'
    ]
    ordering_fields = [
        'codename',
        'content_type__id',
        'group__name',
        'id',
        'name'
    ]
    ordering = 'content_type'


class GroupViewSet(ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    filterset_fields = {
        'guid': ['exact'],
        'created_at': ['exact'],
        'created_by': ['exact'],
        'updated_at': ['exact'],
        'updated_by': ['exact'],
        'name': ['exact'],
        'permissions__codename': ['exact'],
        'user__guid': ['exact']
    }
    search_fields = ['guid', 'name', 'permissions__codename', 'user__guid']
    ordering_fields = [
        'guid',
        'created_at',
        'created_by',
        'updated_at',
        'updated_by',
        'name',
        'permissions__codename',
        'user__guid'
    ]
    ordering = 'name'

    perms_map = {
        'GET': [],
        'OPTIONS': [],
        'HEAD': [],
        'POST': ['add_group'],
        'PUT': ['change_group'],
        'PATCH': ['change_group'],
        'DELETE': ['delete_group'],
    }

    @action(methods=["patch"], detail=True)
    def add_permissions(self, request, pk=None):
        perms_serializer = AddRemovePermissionsSerializer(data=request.data)
        perms_serializer.is_valid(raise_exception=True)

        try:
            our_group = get_object_or_404(self.get_queryset(), pk=pk)
            our_group.add_permissions_to_group(
                perms_serializer.validated_data["permissions"]
                )

            our_group.refresh_from_db()
            our_data = self.get_serializer(our_group).data

            return Response(
                data={"message": "Successful", "detail": our_data},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                data={"message": "Unsuccessful", "detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(methods=['patch'], detail=True)
    def remove_permissions(self, request, pk=None):
        perms_serializer = AddRemovePermissionsSerializer(data=request.data)
        perms_serializer.is_valid(raise_exception=True)

        try:
            our_group = get_object_or_404(self.get_queryset(), pk=pk)
            our_group.remove_permissions_from_group(
                perms_serializer.validated_data["permissions"]
            )

            our_group.refresh_from_db()
            our_data = self.get_serializer(our_group).data

            return Response(
                data={"message": "Successful", "detail": our_data},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            LOGGER.exception(str(e))
            return Response(
                data={"message": "Unsuccessful", "detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(methods=["patch"], detail=True)
    def add_user(self, request, pk=None):
        user_serializer = AddRemoveUserSerializer(data=request.data)
        user_serializer.is_valid(raise_exception=True)

        try:
            our_group = get_object_or_404(self.get_queryset(), pk=pk)
            our_group.add_user_to_group(
                user_serializer.validated_data["user_guid"]
            )

            our_group.refresh_from_db()
            our_data = self.get_serializer(our_group).data

            return Response(
                data={"message": "Successful", "detail": our_data},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            LOGGER.exception(str(e))
            return Response(
                data={"message": "Unsuccessful", "detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(methods=["patch"], detail=True)
    def remove_user(self, request, pk=None):
        user_serializer = AddRemoveUserSerializer(data=request.data)
        user_serializer.is_valid()

        try:
            our_group = get_object_or_404(self.get_queryset(), pk=pk)
            our_group.remove_user_from_group(
                user_serializer.validated_data["user_guid"]
            )

            our_group.refresh_from_db()
            our_data = self.get_serializer(our_group).data

            return Response(
                data={"message": "Successful", "detail": our_data},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            LOGGER.exception(str(e))
            return Response(
                data={"message": "Unsuccessful", "detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class PersonViewSet(ModelViewSet):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    filterset_fields = {
        'guid': ['exact'],
        'created_at': ['exact'],
        'created_by': ['exact'],
        'updated_at': ['exact'],
        'updated_by': ['exact'],
        'first_name': ['exact'],
        'last_name': ['exact'],
        'gender': ['exact'],
        'date_of_birth': ['exact'],
        'phone': ['exact'],
        'address': ['exact'],
        'account_status': ['exact'],
        'user__guid': ['exact'],
    }
    search_fields = [
        'guid',
        'first_name',
        'last_name',
        'gender',
        'date_of_birth',
        'phone',
        'address',
        'account_status',
        'user__guid'
    ]
    ordering_fields = [
        'guid',
        'created_at',
        'created_by',
        'updated_at',
        'updated_by',
        'first_name',
        'last_name',
        'gender',
        'date_of_birth',
        'phone',
        'address',
        'account_status',
        'user__guid'
    ]
    ordering = 'created_at'

    perms_map = {
        'GET': [],
        'OPTIONS': [],
        'HEAD': [],
        'POST': ['add_person'],
        'PUT': ['change_person'],
        'PATCH': ['change_person'],
        'DELETE': ['delete_person'],
    }

    @action(methods=['patch'], detail=True)
    def add_user(self, request, pk=None):
        user_serializer = AddRemoveUserSerializer(data=request.data)
        user_serializer.is_valid(raise_exception=True)

        try:
            person = get_object_or_404(self.get_queryset(), pk=pk)

            person.add_user(user=user_serializer.validated_data["user_guid"])

            person.refresh_from_db()
            person_data = self.get_serializer(person).data

            return Response(
                data={"message": "Successful", "detail": person_data},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            # LOGGER.exception(str(e))
            return Response(
                data={"message": "Unsuccessful", "detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(methods=['patch'], detail=True)
    def remove_user(self, request, pk=None):
        try:
            person = get_object_or_404(self.get_queryset(), pk=pk)
            person.remove_user()

            person.refresh_from_db()
            person_data = self.get_serializer(person).data

            return Response(
                data={"message": "Successful", "detail": person_data},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            # LOGGER.exception(str(e))
            return Response(
                data={"message": "Unsuccessful", "detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(methods=['patch'], detail=True)
    def add_phone(self, request, pk=None):
        phone_serializer = PhoneSerializer(data=request.data)
        phone_serializer.is_valid(raise_exception=True)

        try:
            person = get_object_or_404(self.get_queryset(), pk=pk)
            person.add_phone(phone_serializer.validated_data)

            person.refresh_from_db()
            person_data = self.get_serializer(person).data

            return Response(
                data={"message": "Successful", "detail": person_data},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            LOGGER.exception(str(e))

            return Response(
                data={"message": "Unsuccessful", "detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(methods=['patch'], detail=True)
    def remove_phone(self, request, pk=None):
        phone_serializer = RemovePhoneSerializer(data=request.data)
        phone_serializer.is_valid(raise_exception=True)

        try:
            person = get_object_or_404(self.get_queryset(), pk=pk)
            person.remove_phone(phone_serializer.validated_data)

            person.refresh_from_db()
            person_data = self.get_serializer(person).data

            return Response(
                data={"message": "Successful", "detail": person_data},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            LOGGER.exception(str(e))

            return Response(
                data={"message": "Unsuccessful", "detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(methods=['patch'], detail=True)
    def add_address(self, request, pk=None):
        address_serializer = AddressSerializer(data=request.data)
        address_serializer.is_valid(raise_exception=True)

        try:
            person = get_object_or_404(self.get_queryset(), pk=pk)
            person.add_address(address_serializer.validated_data)

            person.refresh_from_db()
            person_data = self.get_serializer(person).data

            return Response(
                data={"message": "Successful", "detail": person_data},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            LOGGER.exception(str(e))

            return Response(
                data={"message": "Unsuccessful", "detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(methods=['patch'], detail=True)
    def remove_address(self, request, pk=None):
        address_serializer = RemoveAddressSerializer(data=request.data)
        address_serializer.is_valid(raise_exception=True)

        try:
            person = get_object_or_404(self.get_queryset(), pk=pk)
            person.remove_address(address_serializer.validated_data)

            person.refresh_from_db()
            person_data = self.get_serializer(person).data

            return Response(
                data={"message": "Successful", "detail": person_data},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            LOGGER.exception(str(e))

            return Response(
                data={"message": "Unsuccessful", "detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class AddressViewSet(ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    filterset_fields = {
        'guid': ['exact'],
        'created_at': ['exact'],
        'created_by': ['exact'],
        'updated_at': ['exact'],
        'updated_by': ['exact'],
        'address': ['exact']
    }
    search_fields = [
        'guid',
        'address'
    ]
    ordering_fields = [
        'guid',
        'created_at',
        'created_by',
        'updated_at',
        'updated_by',
        'address'
    ]
    ordering = 'created_at'

    perms_map = {
        'GET': [],
        'OPTIONS': [],
        'HEAD': [],
        'POST': ['add_address'],
        'PUT': ['change_address'],
        'PATCH': ['change_address'],
        'DELETE': ['delete_address'],
    }


class PhoneViewSet(ModelViewSet):
    queryset = Phone.objects.all()
    serializer_class = PhoneSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    filterset_fields = {
        'guid': ['exact'],
        'created_at': ['exact'],
        'created_by': ['exact'],
        'updated_at': ['exact'],
        'updated_by': ['exact'],
        'number': ['exact']
    }
    search_fields = [
        'guid',
        'number'
    ]
    ordering_fields = [
        'guid',
        'created_at',
        'created_by',
        'updated_at',
        'updated_by',
        'number'
    ]
    ordering = 'created_at'

    perms_map = {
        'GET': [],
        'OPTIONS': [],
        'HEAD': [],
        'POST': ['add_phone'],
        'PUT': ['change_phone'],
        'PATCH': ['change_phone'],
        'DELETE': ['delete_phone'],
    }
