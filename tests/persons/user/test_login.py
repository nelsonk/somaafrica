import pytest
from django.urls import reverse


class TestLogin:
    @pytest.fixture(autouse=True)
    def create_test_user(self, django_user_model):
        django_user_model.objects.create_user(
            username="testuser",
            email="testuser@tests.com",
            password="testuser"
        )

    def test_login_with_username(self, client):
        credentials = {
            "username": "testuser",
            "password": "testuser"
        }

        response = client.post(reverse("login"), credentials)

        assert response.status_code == 200
        assert "Successful" in response.json()["message"]

    def test_login_with_email(self, client):
        credentials = {
            "username": "testuser@tests.com",
            "password": "testuser"
        }

        response = client.post(reverse("login"), credentials)

        assert response.status_code == 200
        assert "Successful" in response.json()["message"]

    def test_invalid_password(self, client):
        credentials = {
            "username": "testuser",
            "password": "test"
        }

        response = client.post(reverse("login"), credentials)

        assert response.status_code == 400
        assert "Invalid password" in response.json()["detail"]

    def test_user_not_found(self, client):
        credentials = {
            "username": "test",
            "password": "test"
        }

        response = client.post(reverse("login"), credentials)

        assert response.status_code == 400
        assert "does not exist" in response.json()["detail"]

    def test_username_missing(self, client):
        credentials = {
            "password": "test"
        }

        response = client.post(reverse("login"), credentials)

        assert response.status_code == 400
        assert "field is required" in response.json()["username"][0]

    def test_password_missing(self, client):
        credentials = {
            "username": "test"
        }

        response = client.post(reverse("login"), credentials)

        assert response.status_code == 400
        assert "field is required" in response.json()["password"][0]

    def test_username_password_missing(self, client):
        response = client.post(reverse("login"))

        assert response.status_code == 400
        assert "field is required" in response.json()["username"][0]
        assert "field is required" in response.json()["password"][0]

    def test_username_password_empty(self, client):
        credentials = {
            "username": "",
            "password": ""
        }

        response = client.post(reverse("login"), credentials)

        assert response.status_code == 400
        assert "field may not be blank" in response.json()["username"][0]
        assert "field may not be blank" in response.json()["password"][0]

    def test_login_with_non_post(self, client):
        credentials = {
            "username": "testuser",
            "password": "testuser"
        }

        response = client.get(reverse("login"), credentials)

        assert response.status_code == 405
        assert 'Method "GET" not allowed' in response.json()["detail"]

    def test_login_with_more_fields(self, client):
        data = {
            "username": "testuser",
            "password": "testuser",
            "password2": "test",
            "email": "test@tests.com",
            "address": "kampala"
        }

        response = client.post(reverse("login"), data)
        print(response.json())

        assert response.status_code == 200
        assert "Successful" in response.json()["message"]
