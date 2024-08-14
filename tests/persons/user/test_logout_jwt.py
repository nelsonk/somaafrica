import time

import pytest
from django.urls import reverse


class TestLogoutJWT:
    @pytest.fixture
    def create_test_user(self, django_user_model):
        data = {
            "username": "testuser",
            "password": "testuser123"
        }

        django_user_model.objects.create_user(**data)

    @pytest.fixture(autouse=True)
    def create_token(self, create_test_user, client):
        data = {
            "username": "testuser",
            "password": "testuser123"
        }

        self.response = client.post(reverse("token_obtain_pair"), data)

    def test_with_right_access_refresh_token(self, client):
        tokens = self.response.json()
        access_token = tokens["access"]
        refresh_token = tokens["refresh"]
        print(tokens)
        data = {
            "refresh": refresh_token
        }
        headers = {
            "HTTP_AUTHORIZATION": f"Bearer {access_token}"
        }

        response = client.post(reverse("logout-token"), data, **headers)
        print(response.json())

        assert response.status_code == 200
        assert "blacklisted, Successfully" in response.json()["detail"]

    def test_with_wrong_refresh_token(self, client):
        token = {
            "refrsh": "hgahjahkjkashiakwykuwiuwbbjcbbcbkuscblcsihwuhcbubcbnaj"
        }
        access_token = self.response.json()["access"]
        headers = {
            "HTTP_AUTHORIZATION": f"Bearer {access_token}"
        }

        response = client.post(reverse("logout-token"), token, **headers)
        print(response.json())

        assert response.status_code == 400
        assert "Failed" in response.json()["detail"]

    def test_with_expired_refresh_token(self, settings, client):
        tokens = self.response.json()
        access_token = tokens["access"]
        refresh_token = tokens["refresh"]
        headers = {
            "HTTP_AUTHORIZATION": F"Bearer {access_token}"
        }
        data = {
            "refresh": refresh_token
        }
        time.sleep(
            int(
                settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()
            ) + 1
        )

        response = client.post(reverse("logout-token"), data, **headers)
        print(response.json())

        assert response.status_code == 401
        assert "token not valid" in response.json()["detail"]

    def test_with_no_refresh_token(self, client):
        access_token = self.response.json()["access"]
        headers = {
            "HTTP_AUTHORIZATION": f"Bearer {access_token}"
        }

        response = client.post(reverse("logout-token"), **headers)
        print(response.json())

        assert response.status_code == 400
        assert "Failed" in response.json()["detail"]

    def test_with_refresh_token_empty(self, client):
        access_token = self.response.json()["access"]
        headers = {
            "HTTP_AUTHORIZATION": f"Bearer {access_token}"
        }
        data = {
            "refresh": ""
        }

        response = client.post(reverse("logout-token"), data, **headers)
        print(response.json())

        assert response.status_code == 400
        assert "Failed" in response.json()["detail"]

    def test_with_expired_access_token(self, settings, client):
        tokens = self.response.json()
        access_token = tokens["access"]
        refresh_token = tokens["refresh"]
        headers = {
            "HTTP_AUTHORIZATION": F"Bearer {access_token}"
        }
        data = {
            "refresh": refresh_token
        }
        time.sleep(
            int(
                settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds()
            ) + 1
        )

        response = client.post(reverse("logout-token"), data, **headers)
        print(response.json())

        assert response.status_code == 401
        assert "token not valid" in response.json()["detail"]

    def test_with_no_access_token(self, settings, client):
        refresh_token = self.response.json()["refresh"]
        data = {
            "refresh": refresh_token
        }

        response = client.post(reverse("logout-token"), data)
        print(response.json())

        assert response.status_code == 401
        assert "credentials were not provided" in response.json()["detail"]

    def test_with_access_token_empty(self, client):
        refresh_token = self.response.json()["refresh"]
        headers = {
            "HTTP_AUTHORIZATION": "Bearer "
        }
        data = {
            "refresh": refresh_token
        }

        response = client.post(reverse("logout-token"), data, **headers)
        print(response.json())

        assert response.status_code == 401
        assert "bad_authorization_header" in response.json()["code"]

    def test_with_wrong_access_token(self, client):
        refresh_token = self.response.json()["refresh"]
        token = {
            "refrsh": refresh_token
        }
        headers = {
            "HTTP_AUTHORIZATION": "Bearer hshjshjsjkkjsabbjbcacbhahcjvha2jy7"
        }

        response = client.post(reverse("logout-token"), token, **headers)
        print(response.json())

        assert response.status_code == 401
        assert "token not valid" in response.json()["detail"]
