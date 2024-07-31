import re

from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User


class SomaAfricaBackend(BaseBackend):
    def authenticate(self, request, **kwargs):
        username = kwargs["username"]
        password = kwargs["password"]

        if not username or not password:
            return None

        if self.is_email(username):
            user_field = {"email": username}
        else:
            user_field = {"username": username}

        try:
            user = User.objects.get(**user_field)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    def is_email(self, input_string):
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return re.match(pattern, input_string) is not None
