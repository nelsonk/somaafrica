import pytest
from django.urls import reverse, exceptions


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

    def test_delete_own_user(self, client):
        tokens = self.response.json()
        access_token = tokens["access"]
        headers = {
            "HTTP_AUTHORIZATION": f"Bearer {access_token}"
        }

        response = client.delete(
            reverse(
                "user-delete",
                kwargs={"pk": self.user.id}
            ),
            **headers
        )
        print(response.json())

        assert response.status_code == 200
        assert "1 User deleted" in response.json()["message"]

    def test_delete_other_user_as_superuser(self, client):
        tokens = self.response1.json()
        access_token = tokens["access"]
        headers = {
            "HTTP_AUTHORIZATION": f"Bearer {access_token}"
        }

        response = client.delete(
            reverse(
                "user-delete",
                kwargs={"pk": self.user.id}
            ),
            **headers
        )
        print(response.json())

        assert response.status_code == 200
        assert "1 User deleted" in response.json()["message"]

    def test_delete_other_user_with_normaluser_token(self, client):
        tokens = self.response.json()
        access_token = tokens["access"]
        headers = {
            "HTTP_AUTHORIZATION": f"Bearer {access_token}"
        }

        response = client.delete(
            reverse(
                "user-delete",
                kwargs={"pk": self.user1.id}
            ),
            **headers
        )
        print(response.json())

        assert response.status_code == 200
        assert "0 User deleted" in response.json()["message"]

    def test_delete_with_no_token(self, client):
        response = client.delete(
            reverse(
                "user-delete",
                kwargs={"pk": self.user.id}
            ),
        )
        print(response.json())

        assert response.status_code == 401
        assert "credentials were not provided" in response.json()["detail"]

    def test_delete_with_wrong_token(self, client):
        access_token = "sjsjsjjsskaskskoaoaoakakkakjhdfuyebhdb"
        headers = {
            "HTTP_AUTHORIZATION": f"Bearer {access_token}"
        }

        response = client.delete(
            reverse(
                "user-delete",
                kwargs={"pk": self.user.id}
            ),
            **headers
        )
        print(response.json())

        assert response.status_code == 401
        assert "token not valid" in response.json()["detail"]

    def test_delete_with_pk_missing(self, client):
        tokens = self.response.json()
        access_token = tokens["access"]
        headers = {
            "HTTP_AUTHORIZATION": f"Bearer {access_token}"
        }

        with pytest.raises(exceptions.NoReverseMatch):
            client.delete(
                reverse(
                    "user-delete",
                ),
                **headers
            )

    def test_invalid_pk(self, client):
        tokens = self.response.json()
        access_token = tokens["access"]
        headers = {
            "HTTP_AUTHORIZATION": f"Bearer {access_token}"
        }

        response = client.delete(
            reverse(
                "user-delete",
                kwargs={"pk": "sjjsjksjsjkaakjkjaauwuw"}
            ),
            **headers
        )
        print(response.json())

        assert response.status_code == 400
        assert "Unsuccessful" in response.json()["message"]
