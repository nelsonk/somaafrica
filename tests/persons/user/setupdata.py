import abc

from django.test import TestCase
from model_bakery import baker
from rest_framework import status


class SetUpData(TestCase, metaclass=abc.ABCMeta):
    model = None

    @classmethod
    def setUpTestData(cls):
        cls.normal_user = baker.make(
            'persons.User',
            make_m2m=True,
            username="testuser",
            email="testuser@tests.com"
        )
        cls.normal_user.set_password("testuser")
        cls.normal_user.save()

        cls.super_user = baker.make(
            'persons.User',
            make_m2m=True,
            username="2user",
            is_staff=True,
            is_superuser=True
        )
        cls.super_user.set_password("2user")
        cls.super_user.save()

        cls.logins = {
            "username": "testuser@tests.com",
            "password": "testuser"
        }
        cls.super_logins = {
            "username": "2user",
            "password": "2user"
        }

        assert cls.normal_user is not None, "Normal user was not created."
        assert cls.super_user is not None, "Superuser was not created."

    def setUp(self):
        """This method should be customized in the child class"""
        if self.model is None:
            raise NotImplementedError(
                "Subclasses must define 'model' and related attributes."
            )

        self.data = baker.prepare(self.model).__dict__
        self.data.pop('_state', None)
        self.data.pop('guid', None)

        self.persistent_data = baker.make(
            self.model,
            _quantity=5,
            make_m2m=True
        )

        self.tokens = self.client.post(
            '/token',
            data=self.logins,
            content_type='application/json'
        )
        self.access_token = self.tokens.json()["access"]
        self.login_headers = {
            "HTTP_AUTHORIZATION": f"Bearer {self.access_token}"
        }

        self.super_tokens = self.client.post(
            '/token',
            data=self.super_logins,
            content_type='application/json'
        )
        self.super_access_token = self.super_tokens.json()["access"]
        self.super_login_headers = {
            "HTTP_AUTHORIZATION": f"Bearer {self.super_access_token}"
        }

        real_pk = self.persistent_data[4].guid
        fake_pk = "hjssjjsksnskjkbbkskjshkjkjsjhksjk"
        self.test_cases = [
            (self.login_headers, real_pk, status.HTTP_403_FORBIDDEN),
            (self.super_login_headers, real_pk, status.HTTP_200_OK),
            (self.super_login_headers, fake_pk, status.HTTP_400_BAD_REQUEST)
        ]
