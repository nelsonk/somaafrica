from django.test import TestCase
from django.urls import reverse

from model_bakery import baker


class TestLogoutJWT(TestCase):
    @classmethod
    def setUpTestData(cls):
        data = baker.make(
            'persons.User',
            make_m2m=True,
            username="testuser",
            email="testuser@tests.com"
        )
        data.set_password("testuser")
        data.save()

        cls.data = {
            "username": data.username,
            "password": "testuser"
        }

    def setUp(self):
        self.response = self.client.post(
            reverse("token_obtain_pair"),
            self.data
        )
        refresh_token = self.response.json()["refresh"]
        self.token_data = {
            "refresh": refresh_token
        }

        access_token = self.response.json()["access"]
        self.login_headers = {
            "HTTP_AUTHORIZATION": f"Bearer {access_token}"
        }
        return self.response.json()

    def test_with_right_access_refresh_token(self):
        response = self.client.post(
            reverse("logout-token"),
            self.token_data,
            **self.login_headers
        )
        print(response.json())

        self.assertContains(
            response,
            "blacklisted, Successfully",
            status_code=200
        )

    def test_with_wrong_refresh_token(self):
        token = {
            "refresh": "hgahjahkjkashiakwykuwiuwbbjcbbcbkuscblcsihwuhcbubcbnaj"
        }

        response = self.client.post(
            reverse("logout-token"),
            token,
            **self.login_headers
        )
        print(response.json())

        self.assertContains(
            response,
            "Failed",
            status_code=400
        )

    def test_with_expired_refresh_token(self):
        self.client.post(
            reverse('logout-token'),
            self.token_data,
            **self.login_headers
        )

        response = self.client.post(
            reverse("logout-token"),
            self.token_data,
            **self.login_headers
        )
        print(response.json())

        self.assertContains(
            response,
            "Token is blacklisted",
            status_code=400
        )

    def test_with_no_refresh_token(self):
        response = self.client.post(
            reverse("logout-token"),
            **self.login_headers
        )
        print(response.json())

        self.assertContains(
            response,
            "field is required",
            status_code=400
        )

    def test_with_refresh_token_empty(self):
        data = {
            "refresh": ""
        }

        response = self.client.post(
            reverse("logout-token"),
            data,
            **self.login_headers
        )
        print(response.json())

        self.assertContains(
            response,
            "field may not be blank",
            status_code=400
        )

    def test_with_no_access_token(self):
        response = self.client.post(reverse("logout-token"), self.token_data)
        print(response.json())

        self.assertContains(
            response,
            "credentials were not provided",
            status_code=401
        )

    def test_with_access_token_empty(self):
        headers = {
            "HTTP_AUTHORIZATION": "Bearer "
        }

        response = self.client.post(
            reverse("logout-token"),
            self.token_data,
            **headers
        )
        print(response.json())

        self.assertContains(
            response,
            "bad_authorization_header",
            status_code=401
        )

    def test_with_wrong_access_token(self):
        headers = {
            "HTTP_AUTHORIZATION": "Bearer hshjshjsjkkjsabbjbcacbhahcjvha2jy7"
        }

        response = self.client.post(
            reverse("logout-token"),
            self.token_data,
            **headers
        )
        print(response.json())

        self.assertContains(
            response,
            "token not valid",
            status_code=401
        )
