from django.test import TestCase
from django.urls import reverse


class TestSignup(TestCase):
    def test_signup_with_username(self):
        data = {
            "username": "testuser",
            "password1": "testuser1",
            "password2": "testuser1"
        }

        response = self.client.post(reverse("signup"), data)

        self.assertContains(response, "Successful", status_code=200)

    def test_signup_with_email(self):
        data = {
            "email": "testuser@tests.com",
            "password1": "testuser1",
            "password2": "testuser1"
        }

        response = self.client.post(reverse("signup"), data)
        print(response.json())

        self.assertContains(response, "Successful", status_code=200)

    def test_signup_with_username_email(self):
        data = {
            "username": "testuser",
            "email": "testuser@tests.com",
            "password1": "testuser1",
            "password2": "testuser1"
        }

        response = self.client.post(reverse("signup"), data)
        print(response.json())

        self.assertContains(response, "Successful", status_code=200)

    def test_signup_with_username_email_missing(self):
        data = {
            "password1": "testuser1",
            "password2": "testuser12"
        }

        response = self.client.post(reverse("signup"), data)
        print(response.json())

        self.assertContains(
            response,
            "Username or Email required",
            status_code=406
        )

    def test_signup_with_wrong_email_format(self):
        data = {
            "email": "testuser@test",
            "password1": "test",
            "password2": "test"
        }

        response = self.client.post(reverse("signup"), data)

        self.assertContains(
            response,
            "Enter a valid email address",
            status_code=406
        )

    def test_signup_with_one_password(self):
        data = {
            "username": "testuser1",
            "password2": "testuser12"
        }

        response = self.client.post(reverse("signup"), data)
        print(response.json())

        self.assertContains(
            response,
            "This field is required",
            status_code=406
        )

    def test_signup_mismatched_passwords(self):
        data = {
            "email": "testuser@tests.com",
            "password1": "testuser1",
            "password2": "testuser12"
        }

        response = self.client.post(reverse("signup"), data)
        print(response.json())

        self.assertContains(
            response,
            "Password mismatch",
            status_code=406
        )

    def test_signup_with_no_data(self):
        response = self.client.post(reverse("signup"))
        print(response.json())

        self.assertContains(
            response,
            "This field is required",
            status_code=406
        )

    def test_signup_with_empty_data(self):
        data = {
            "username": "",
            "password1": "",
            "password2": ""
        }

        response = self.client.post(reverse("signup"), data)
        print(response.json())

        self.assertContains(
            response,
            "field may not be blank",
            status_code=406
        )

    def test_signup_with_more_fields(self):
        data = {
            "username": "test",
            "password1": "test",
            "password2": "test",
            "email": "test@tests.com",
            "address": "kampala"
        }

        response = self.client.post(reverse("signup"), data)
        print(response.json())

        self.assertContains(response, "Successful", status_code=200)

    def test_singup_with_wrong_method(self):
        data = {
            "username": "test",
            "password1": "test",
            "password2": "test"
        }

        response = self.client.get(reverse("signup"), data)
        print(response.json())

        self.assertContains(
            response,
            'not allowed',
            status_code=405
        )
