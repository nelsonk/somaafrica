from django.test import TestCase

from somaafrica.commons.authentication_backends import raw_authenticate


class TestAuthenticationBackends(TestCase):
    def test_authenticate_username_password_none(self):
        authenticated_user = raw_authenticate(None, None)
        assert authenticated_user is None
