import time

import pytest
from django.urls import reverse


class TestRefreshToken:
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
        return self.response.json()

    def test_with_right_refresh_token(self, client):
        tokens = self.response.json()
        refresh_token = tokens["refresh"]
        print(tokens)
        data = {
            "refresh": refresh_token
        }

        response = client.post(reverse("token_refresh"), data)
        print(response.json())

        assert response.status_code == 200
        assert response.json()["access"] is not None
        assert response.json()["refresh"] is not None

    def test_with_wrong_refresh_token(self, client):
        token = {
            "refresh": "hgahjahkjkashiakwykuwiuwbbjcbbcbkuscblcsihwuhcbubcbnaj"
        }

        response = client.post(reverse("token_refresh"), token)
        print(response.json())

        assert response.status_code == 401
        assert "Token is invalid or expired" in response.json()["detail"]

    def test_with_expired_refresh_token(self, settings, client):
        tokens = self.response.json()
        refresh_token = tokens["refresh"]
        data = {
            "refresh": refresh_token
        }
        time.sleep(
            int(
                settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()
            ) + 1
        )

        response = client.post(reverse("token_refresh"), data)
        print(response.json())

        assert response.status_code == 401
        assert "Token is invalid or expired" in response.json()["detail"]

    def test_with_no_refresh_token(self, client):
        response = client.post(reverse("token_refresh"))
        print(response.json())

        assert response.status_code == 400
        assert "field is required" in response.json()["refresh"][0]

    def test_with_refresh_token_empty(self, client):
        data = {
            "refresh": ""
        }

        response = client.post(reverse("token_refresh"), data)
        print(response.json())

        assert response.status_code == 400
        assert "field may not be blank" in response.json()["refresh"][0]
