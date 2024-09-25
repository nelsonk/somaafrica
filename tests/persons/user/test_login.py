from django.test import TestCase
from django.urls import reverse
from model_bakery import baker


class TestLogin(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = baker.make(
            'persons.User',
            username="testuser",
            email="testuser@tests.com"
        )
        user.set_password("testuser")
        user.save()

    def test_login_with_username(self):
        credentials = {
            "username": "testuser",
            "password": "testuser"
        }

        response = self.client.post(reverse("login"), credentials)

        self.assertContains(response, "Successful", status_code=200)

    def test_login_with_email(self):
        credentials = {
            "username": "testuser@tests.com",
            "password": "testuser"
        }

        response = self.client.post(reverse("login"), credentials)

        self.assertContains(response, "Successful", status_code=200)

    def test_invalid_password(self):
        credentials = {
            "username": "testuser",
            "password": "test"
        }

        response = self.client.post(reverse("login"), credentials)

        self.assertContains(response, "Invalid password", status_code=400)

    def test_user_not_found(self):
        credentials = {
            "username": "test",
            "password": "test"
        }

        response = self.client.post(reverse("login"), credentials)

        self.assertContains(response, "does not exist", status_code=400)

    def test_username_missing(self):
        credentials = {
            "password": "test"
        }

        response = self.client.post(reverse("login"), credentials)

        self.assertContains(response, "field is required", status_code=400)

    def test_password_missing(self):
        credentials = {
            "username": "test"
        }

        response = self.client.post(reverse("login"), credentials)

        self.assertContains(response, "field is required", status_code=400)

    def test_username_password_missing(self):
        response = self.client.post(reverse("login"))

        self.assertEqual(response.status_code, 400)
        self.assertTrue("field is required" in response.json()["username"][0])
        self.assertTrue("field is required" in response.json()["password"][0])

    def test_username_password_empty(self):
        credentials = {
            "username": "",
            "password": ""
        }

        response = self.client.post(reverse("login"), credentials)

        self.assertEqual(response.status_code, 400)
        self.assertTrue(
            "field may not be blank" in response.json()["username"][0]
        )
        self.assertTrue(
            "field may not be blank" in response.json()["password"][0]
        )

    def test_login_with_non_post(self):
        credentials = {
            "username": "testuser",
            "password": "testuser"
        }

        response = self.client.get(reverse("login"), credentials)

        self.assertContains(response, "not allowed", status_code=405)

    def test_login_with_more_fields(self):
        data = {
            "username": "testuser",
            "password": "testuser",
            "password2": "test",
            "email": "test@tests.com",
            "address": "kampala"
        }

        response = self.client.post(reverse("login"), data)
        print(response.json())

        self.assertContains(response, "Successful", status_code=200)
