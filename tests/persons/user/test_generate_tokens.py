import pytest
from django.urls import reverse

from somaafrica.commons.authentication_backends import AuthenticationError


class TestGenerateTokens:
    @pytest.fixture(autouse=True)
    def create_test_user(self, django_user_model):
        data = {
            "username": "testuser",
            "email": "testuser@tests.com",
            "password": "testuser123"
        }

        django_user_model.objects.create_user(**data)

    def test_with_right_credentials(self, client):
        data = {
            "username": "testuser",
            "password": "testuser123"
        }

        response = client.post(reverse("token_obtain_pair"), data)

        assert response.status_code == 200
        assert response.json()["access"] is not None
        assert response.json()["refresh"] is not None

    def test_with_wrong_username(self, django_user_model, client):
        data = {
            "username": "testuser1",
            "password": "testuser123"
        }

        with pytest.raises(django_user_model.DoesNotExist):
            response = client.post(reverse("token_obtain_pair"), data)
            print(response.json())

    def test_with_wrong_password(self, client):
        data = {
            "username": "testuser",
            "password": "testuser1"
        }

        with pytest.raises(AuthenticationError):
            response = client.post(reverse("token_obtain_pair"), data)
            print(response.json())

    def test_with_no_password(self, client):
        data = {
            "username": "testuser",
        }

        response = client.post(reverse("token_obtain_pair"), data)
        print(response.json())

        assert response.status_code == 400
        assert "field is required" in response.json()["password"][0]

    def test_with_no_username(self, client):
        data = {
            "password": "testuser",
        }

        response = client.post(reverse("token_obtain_pair"), data)
        print(response.json())

        assert response.status_code == 400
        assert "field is required" in response.json()["username"][0]

    def test_with_username_empty(self, client):
        data = {
            "password": "testuser",
            "username": ""
        }

        response = client.post(reverse("token_obtain_pair"), data)
        print(response.json())

        assert response.status_code == 400
        assert "field may not be blank" in response.json()["username"][0]

    def test_with_password_empty(self, client):
        data = {
            "password": "",
            "username": "testuser"
        }

        response = client.post(reverse("token_obtain_pair"), data)
        print(response.json())

        assert response.status_code == 400
        assert "field may not be blank" in response.json()["password"][0]

    def test_with_no_credentials(self, client):
        response = client.post(reverse("token_obtain_pair"))
        print(response.json())

        assert response.status_code == 400
        assert "field is required" in response.json()["username"][0]
        assert "field is required" in response.json()["password"][0]

    def test_with_email(self, client):
        data = {
            "username": "testuser@tests.com",
            "password": "testuser123"
        }

        response = client.post(reverse("token_obtain_pair"), data)

        assert response.status_code == 200
        assert response.json()["access"] is not None
        assert response.json()["refresh"] is not None
