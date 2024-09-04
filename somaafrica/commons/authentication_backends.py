from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from django.db.models import Q


User = get_user_model()


class AuthenticationError(Exception):
    pass


class SomaAfricaBackend(BaseBackend):
    def authenticate(self, request, **kwargs):
        username = kwargs["username"]
        password = kwargs["password"]

        return raw_authenticate(username, password)


def raw_authenticate(username, password):
    if not username or not password:
        return None

    try:
        user = User.objects.get(Q(username=username) | Q(email=username))
        password_mathches = user.check_password(password)

        if password_mathches:
            return user
        raise AuthenticationError("Invalid password")
    except User.DoesNotExist:
        raise
