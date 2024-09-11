import pytest
from django.urls import reverse


@pytest.mark.django_db
class TestSignup:
    def test_signup_with_username(self, client):
        data = {
            "username": "testuser",
            "password1": "testuser1",
            "password2": "testuser1"
        }

        response = client.post(reverse("signup"), data)

        assert response.status_code == 200
        assert "Successful" in response.json()["message"]

    def test_signup_with_email(self, client):
        data = {
            "email": "testuser@tests.com",
            "password1": "testuser1",
            "password2": "testuser1"
        }

        response = client.post(reverse("signup"), data)
        print(response.json())

        assert response.status_code == 200
        assert "Successful" in response.json()["message"]

    def test_signup_with_username_email(self, client):
        data = {
            "username": "testuser",
            "email": "testuser@tests.com",
            "password1": "testuser1",
            "password2": "testuser1"
        }

        response = client.post(reverse("signup"), data)
        print(response.json())

        assert response.status_code == 200
        assert "Successful" in response.json()["message"]

    def test_signup_with_username_email_missing(self, client):
        data = {
            "password1": "testuser1",
            "password2": "testuser12"
        }

        response = client.post(reverse("signup"), data)
        print(response.json())

        assert response.status_code == 406
        assert "Username or Email required" in response.json()["message"]

    def test_signup_with_wrong_email_format(self, client):
        data = {
            "email": "testuser@test",
            "password1": "test",
            "password2": "test"
        }

        response = client.post(reverse("signup"), data)

        assert response.status_code == 406
        assert "Enter a valid email address" in response.json()["message"]

    def test_signup_with_one_password(self, client):
        data = {
            "username": "testuser1",
            "password2": "testuser12"
        }

        response = client.post(reverse("signup"), data)
        print(response.json())

        assert response.status_code == 406
        assert "This field is required" in response.json()["message"]

    def test_signup_mismatched_passwords(self, client):
        data = {
            "email": "testuser@tests.com",
            "password1": "testuser1",
            "password2": "testuser12"
        }

        response = client.post(reverse("signup"), data)
        print(response.json())

        assert response.status_code == 406
        assert "Password mismatch" in response.json()["message"]

    def test_signup_with_no_data(self, client):
        response = client.post(reverse("signup"))
        print(response.json())

        assert response.status_code == 406
        assert "This field is required" in response.json()["message"]

    def test_signup_with_empty_data(self, client):
        data = {
            "username": "",
            "password1": "",
            "password2": ""
        }

        response = client.post(reverse("signup"), data)
        print(response.json())

        assert response.status_code == 406
        assert "field may not be blank" in response.json()["message"]

    def test_signup_with_more_fields(self, client):
        data = {
            "username": "test",
            "password1": "test",
            "password2": "test",
            "email": "test@tests.com",
            "address": "kampala"
        }

        response = client.post(reverse("signup"), data)
        print(response.json())

        assert response.status_code == 200
        assert "Successful" in response.json()["message"]

    def test_singup_with_wrong_method(self, client):
        data = {
            "username": "test",
            "password1": "test",
            "password2": "test"
        }

        response = client.get(reverse("signup"), data)
        print(response.json())

        assert response.status_code == 405
        assert 'Method "GET" not allowed' in response.json()["detail"]
