from django.test import TestCase
from django.urls import reverse

from model_bakery import baker


class TestRefreshToken(TestCase):

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
        response = self.client.post(
            reverse("token_obtain_pair"),
            self.data
        )
        refresh_token = response.json()["refresh"]
        self.token_data = {
            "refresh": refresh_token
        }

        access_token = response.json()["access"]
        self.login_headers = {
            "HTTP_AUTHORIZATION": f"Bearer {access_token}"
        }
        return response.json()

    def test_with_right_refresh_token(self):
        response = self.client.post(reverse("token_refresh"), self.token_data)
        print(response.json())

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["access"] is not None)
        self.assertTrue(response.json()["refresh"] is not None)

    def test_with_wrong_refresh_token(self):
        token = {
            "refresh": "hgahjahkjkashiakwykuwiuwbbjcbbcbkuscblcsihwuhcbubcbnaj"
        }

        response = self.client.post(reverse("token_refresh"), token)
        print(response.json())

        self.assertContains(
            response,
            "Token is invalid or expired",
            status_code=401
        )

    def test_with_expired_refresh_token(self):
        self.client.post(
            reverse('logout-token'),
            self.token_data,
            **self.login_headers
        )

        response = self.client.post(reverse("token_refresh"), self.token_data)
        print(response.json())

        self.assertContains(
            response,
            "token_not_valid",
            status_code=401
        )

    def test_with_no_refresh_token(self):
        response = self.client.post(reverse("token_refresh"))
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

        response = self.client.post(reverse("token_refresh"), data)
        print(response.json())

        self.assertContains(
            response,
            "field may not be blank",
            status_code=400
        )
