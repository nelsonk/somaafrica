import pytest
from django.urls import reverse


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

    def test_own_details(self, client):
        tokens = self.response.json()
        access_token = tokens["access"]
        headers = {
            "HTTP_AUTHORIZATION": f"Bearer {access_token}"
        }

        response = client.get(
            reverse("user-detail", kwargs={"pk": self.user.id}),
            **headers
        )
        print(response.json())

        assert response.status_code == 200
        assert "usertest" in response.json()["username"]

    def test_other_user_details_with_superuser_token(self, client):
        tokens = self.response1.json()
        access_token = tokens["access"]
        headers = {
            "HTTP_AUTHORIZATION": f"Bearer {access_token}"
        }

        response = client.get(
            reverse("user-detail", kwargs={"pk": self.user.id}),
            **headers
        )
        print(response.json())

        assert response.status_code == 200
        assert "usertest" in response.json()["username"]

    def test_other_user_details_with_normaluser_token(self, client):
        tokens = self.response.json()
        access_token = tokens["access"]
        headers = {
            "HTTP_AUTHORIZATION": f"Bearer {access_token}"
        }

        response = client.get(
            reverse("user-detail", kwargs={"pk": self.user1.id}),
            **headers
        )
        print(response.json())

        assert response.status_code == 404
        assert "No User matches" in response.json()["detail"]

    def test_with_no_token(self, client):
        response = client.get(
            reverse("user-detail", kwargs={"pk": self.user.id})
        )
        print(response.json())

        assert response.status_code == 401
        assert "credentials were not provided" in response.json()["detail"]

    def test_with_wrong_token(self, client):
        access_token = "sjsjsjjsskaskskoaoaoakakkakjhdfuyebhdb"
        headers = {
            "HTTP_AUTHORIZATION": f"Bearer {access_token}"
        }

        response = client.get(
            reverse("user-detail", kwargs={"pk": self.user.id}),
            **headers
        )
        print(response.json())

        assert response.status_code == 401
        assert "token not valid" in response.json()["detail"]
