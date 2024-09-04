import pytest
from django.urls import reverse

from somaafrica.commons.authentication_backends import raw_authenticate


class TestListUsers:
    @pytest.fixture
    def create_test_user(self, django_user_model):
        data = {
            "username": "usertest",
            "password": "testuser123"
        }
        data1 = {
            "username": "testuser1",
            "password": "testuser123",
            "email": "testuser1@tests.com"
        }

        self.user = django_user_model.objects.create_user(**data)
        self.user1 = django_user_model.objects.create_superuser(**data1)

        self.data = {
            "password1": "password",
            "password2": "password"
        }

    @pytest.fixture(autouse=True)
    def create_token(self, create_test_user, client):
        data = {
            "username": "usertest",
            "password": "testuser123"
        }
        data1 = {
            "username": "testuser1",
            "password": "testuser123"
        }

        self.response = client.post(reverse("token_obtain_pair"), data)
        self.response1 = client.post(reverse("token_obtain_pair"), data1)

    def test_change_own_password(self, client):
        tokens = self.response.json()
        access_token = tokens["access"]
        headers = {
            "HTTP_AUTHORIZATION": f"Bearer {access_token}"
        }

        response = client.put(
            reverse(
                "user-change-password",
                kwargs={"pk": self.user.id}
            ),
            self.data,
            content_type="application/json",
            **headers
        )
        print(response.json())

        assert response.status_code == 200
        assert "usertest" in response.json()["detail"]["username"]

        authenticated_user = raw_authenticate(
            "usertest",
            self.data["password1"]
        )
        assert authenticated_user is not None
        user_model = "<class 'somaafrica.persons.models.User'>"
        assert str(type(authenticated_user)) == user_model
        assert authenticated_user.username == "usertest"

    def test_change_other_user_password_as_superuser(self, client):
        tokens = self.response1.json()
        access_token = tokens["access"]
        headers = {
            "HTTP_AUTHORIZATION": f"Bearer {access_token}"
        }

        response = client.put(
            reverse(
                "user-change-password",
                kwargs={"pk": self.user.id}
            ),
            self.data,
            content_type="application/json",
            **headers
        )
        print(response.json())

        assert response.status_code == 200
        assert "usertest" in response.json()["detail"]["username"]

    def test_other_user_details_with_normaluser_token(self, client):
        tokens = self.response.json()
        access_token = tokens["access"]
        headers = {
            "HTTP_AUTHORIZATION": f"Bearer {access_token}"
        }

        response = client.put(
            reverse(
                "user-change-password",
                kwargs={"pk": self.user1.id}
            ),
            self.data,
            content_type="application/json",
            **headers
        )
        print(response.json())

        assert response.status_code == 400
        assert "No User matches" in response.json()["detail"]

    def test_with_no_token(self, client):
        response = client.put(
            reverse(
                "user-change-password",
                kwargs={"pk": self.user.id}
            ),
            self.data
        )
        print(response.json())

        assert response.status_code == 401
        assert "credentials were not provided" in response.json()["detail"]

    def test_with_wrong_token(self, client):
        access_token = "sjsjsjjsskaskskoaoaoakakkakjhdfuyebhdb"
        headers = {
            "HTTP_AUTHORIZATION": f"Bearer {access_token}"
        }

        response = client.put(
            reverse(
                "user-change-password",
                kwargs={"pk": self.user.id}
            ),
            self.data,
            content_type="application/json",
            **headers
        )
        print(response.json())

        assert response.status_code == 401
        assert "token not valid" in response.json()["detail"]

    def test_password_missing(self, client):
        tokens = self.response.json()
        access_token = tokens["access"]
        headers = {
            "HTTP_AUTHORIZATION": f"Bearer {access_token}"
        }

        response = client.put(
            reverse(
                "user-change-password",
                kwargs={"pk": self.user.id}
            ),
            content_type="application/json",
            **headers
        )
        print(response.json())

        assert response.status_code == 400
        assert "Password null" in response.json()["message"]

    def test_password_mismatch(self, client):
        tokens = self.response.json()
        access_token = tokens["access"]
        headers = {
            "HTTP_AUTHORIZATION": f"Bearer {access_token}"
        }
        data = {
            "password1": "password",
            "password2": "pass"
        }

        response = client.put(
            reverse(
                "user-change-password",
                kwargs={"pk": self.user.id}
            ),
            data,
            content_type="application/json",
            **headers
        )
        print(response.json())

        assert response.status_code == 400
        assert "Password mismatch" in response.json()["message"]
