from django.test import TestCase
from django.urls import reverse
from model_bakery import baker


class TestGenerateTokens(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = baker.make(
            'persons.User',
            username="testuser",
            email="testuser@tests.com"
        )
        user.set_password("testuser123")
        user.save()

    def test_with_right_credentials(self):
        data = {
            "username": "testuser",
            "password": "testuser123"
        }

        response = self.client.post(reverse("token_obtain_pair"), data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["access"] is not None)
        self.assertTrue(response.json()["refresh"] is not None)

    def test_with_wrong_username(self):
        data = {
            "username": "testuser1",
            "password": "testuser123"
        }

        response = self.client.post(reverse("token_obtain_pair"), data)
        print(response.json())

        self.assertContains(
            response,
            "No User matches the given query",
            status_code=400
        )

    def test_with_wrong_password(self):
        data = {
            "username": "testuser",
            "password": "testuser1"
        }

        response = self.client.post(reverse("token_obtain_pair"), data)
        print(response.json())

        self.assertContains(response, "Invalid password", status_code=400)

    def test_with_no_password(self):
        data = {
            "username": "testuser",
        }

        response = self.client.post(reverse("token_obtain_pair"), data)
        print(response.json())

        self.assertContains(response, "field is required", status_code=400)

    def test_with_no_username(self):
        data = {
            "password": "testuser",
        }

        response = self.client.post(reverse("token_obtain_pair"), data)
        print(response.json())

        self.assertContains(response, "field is required", status_code=400)

    def test_with_username_empty(self):
        data = {
            "password": "testuser",
            "username": ""
        }

        response = self.client.post(reverse("token_obtain_pair"), data)
        print(response.json())

        self.assertContains(
            response,
            "field may not be blank",
            status_code=400
        )

    def test_with_password_empty(self):
        data = {
            "password": "",
            "username": "testuser"
        }

        response = self.client.post(reverse("token_obtain_pair"), data)
        print(response.json())

        self.assertContains(
            response,
            "field may not be blank",
            status_code=400
        )

    def test_with_no_credentials(self):
        response = self.client.post(reverse("token_obtain_pair"))
        print(response.json())

        self.assertEqual(response.status_code, 400)
        self.assertTrue("field is required" in response.json()["username"][0])
        self.assertTrue("field is required" in response.json()["password"][0])

    def test_with_email(self):
        data = {
            "username": "testuser@tests.com",
            "password": "testuser123"
        }

        response = self.client.post(reverse("token_obtain_pair"), data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["access"] is not None)
        self.assertTrue(response.json()["refresh"] is not None)
