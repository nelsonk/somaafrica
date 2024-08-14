import pytest
from django.urls import reverse


class TestListUsers:
    @pytest.fixture
    def create_test_user(self, django_user_model):
        data = {
            "username": "testuser",
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
            "username": "testuser",
            "password": "testuser123"
        }
        data1 = {
            "username": "testuser1",
            "password": "testuser123"
        }

        self.response = client.post(reverse("token_obtain_pair"), data)
        self.response1 = client.post(reverse("token_obtain_pair"), data1)

    def test_with_normal_user_token(self, client):
        tokens = self.response.json()
        access_token = tokens["access"]
        headers = {
            "HTTP_AUTHORIZATION": f"Bearer {access_token}"
        }

        response = client.get(reverse("user-list"), **headers)
        print(response.json())

        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_with_superuser_token(self, client):
        tokens = self.response1.json()
        access_token = tokens["access"]
        headers = {
            "HTTP_AUTHORIZATION": f"Bearer {access_token}"
        }

        response = client.get(reverse("user-list"), **headers)
        print(response.json())

        assert response.status_code == 200
        assert len(response.json()) > 1

    def test_with_no_token(self, client):
        response = client.get(reverse("user-list"))
        print(response.json())

        assert response.status_code == 401
        assert "credentials were not provided" in response.json()["detail"]

    def test_with_wrong_token(self, client):
        access_token = "sjsjsjjsskaskskoaoaoakakkakjhdfuyebhdb"
        headers = {
            "HTTP_AUTHORIZATION": f"Bearer {access_token}"
        }

        response = client.get(reverse("user-list"), **headers)
        print(response.json())

        assert response.status_code == 401
        assert "token not valid" in response.json()["detail"]

    def test_with_ordering(self, client):
        tokens = self.response1.json()
        access_token = tokens["access"]
        headers = {
            "HTTP_AUTHORIZATION": f"Bearer {access_token}"
        }
        params = {
            "ordering": "username"
        }

        response = client.get(reverse("user-list"), params, **headers)
        print(response.json())

        assert response.status_code == 200
        assert "testuser" in response.json()[0]["username"]

    def test_with_reverse_ordering(self, client):
        tokens = self.response1.json()
        access_token = tokens["access"]
        headers = {
            "HTTP_AUTHORIZATION": f"Bearer {access_token}"
        }
        params = {
            "ordering": "-username"
        }

        response = client.get(reverse("user-list"), params, **headers)
        print(response.json())

        assert response.status_code == 200
        assert "testuser1" in response.json()[0]["username"]

    def test_with_search_username(self, client):
        tokens = self.response1.json()
        access_token = tokens["access"]
        headers = {
            "HTTP_AUTHORIZATION": f"Bearer {access_token}"
        }
        params = {
            "username": "testuser1"
        }

        response = client.get(reverse("user-list"), params, **headers)
        print(response.json())

        assert response.status_code == 200
        assert "testuser1" in response.json()[0]["username"]

    def test_with_search_email(self, client):
        tokens = self.response1.json()
        access_token = tokens["access"]
        headers = {
            "HTTP_AUTHORIZATION": f"Bearer {access_token}"
        }
        params = {
            "email": "testuser1@tests.com"
        }

        response = client.get(reverse("user-list"), params, **headers)
        print(response.json())

        assert response.status_code == 200
        assert "testuser1" in response.json()[0]["username"]

    def test_with_search_id(self, client):
        tokens = self.response1.json()
        access_token = tokens["access"]
        headers = {
            "HTTP_AUTHORIZATION": f"Bearer {access_token}"
        }
        params = {
            "id": self.user.id
        }

        response = client.get(reverse("user-list"), params, **headers)
        print(response.json())

        assert response.status_code == 200
        assert str(self.user.id) in response.json()[0]["id"]

    def test_with_search_invalid_uuid(self, client):
        tokens = self.response1.json()
        access_token = tokens["access"]
        headers = {
            "HTTP_AUTHORIZATION": f"Bearer {access_token}"
        }
        params = {
            "id": "2"
        }

        response = client.get(reverse("user-list"), params, **headers)
        print(response.json())

        assert response.status_code == 400
        assert "Enter a valid UUID" not in response.json()["id"]

    def test_with_search_id_not_found(self, client):
        tokens = self.response1.json()
        access_token = tokens["access"]
        headers = {
            "HTTP_AUTHORIZATION": f"Bearer {access_token}"
        }
        params = {
            "id": "a43c0664-1ab0-495e-8a0e-75ecb2c09f99"
        }

        response = client.get(reverse("user-list"), params, **headers)
        print(response.json())

        assert response.status_code == 200
        assert len(response.json()) == 0

    def test_with_multiple_filters(self, client):
        tokens = self.response1.json()
        access_token = tokens["access"]
        headers = {
            "HTTP_AUTHORIZATION": f"Bearer {access_token}"
        }
        params = {
            "username": "testuser1",
            "email": "testuser1@tests.com",
            "id": str(self.user1.id)
        }

        response = client.get(reverse("user-list"), params, **headers)
        print(response.json())

        assert response.status_code == 200
        assert "testuser1" in response.json()[0]["username"]

    def test_with_wildcard_search(self, client):
        tokens = self.response1.json()
        access_token = tokens["access"]
        headers = {
            "HTTP_AUTHORIZATION": f"Bearer {access_token}"
        }
        params = {
            "search": "testuser1@tes",
        }

        response = client.get(reverse("user-list"), params, **headers)
        print(response.json())

        assert response.status_code == 200
        assert "testuser1" in response.json()[0]["username"]

    def test_with_wildcard_search_not_found(self, client):
        tokens = self.response1.json()
        access_token = tokens["access"]
        headers = {
            "HTTP_AUTHORIZATION": f"Bearer {access_token}"
        }
        params = {
            "search": "testuser1@tes1",
        }

        response = client.get(reverse("user-list"), params, **headers)
        print(response.json())

        assert response.status_code == 200
        assert len(response.json()) == 0

    def test_with_wildcard_search_not_own_not_superuser(self, client):
        tokens = self.response.json()
        access_token = tokens["access"]
        headers = {
            "HTTP_AUTHORIZATION": f"Bearer {access_token}"
        }
        params = {
            "search": "testuser1@tes",
        }

        response = client.get(reverse("user-list"), params, **headers)
        print(response.json())

        assert response.status_code == 200
        assert len(response.json()) == 0
