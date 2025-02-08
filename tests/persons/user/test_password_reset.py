from django.test import TestCase
from django.urls import reverse

from model_bakery import baker
from rest_framework import status

from somaafrica.commons.authentication_backends import raw_authenticate


class TestListUsers(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.normal_user = baker.make(
            'persons.User',
            make_m2m=True,
            username="testuser",
            email="testuser@tests.com"
        )
        cls.normal_user.set_password("testuser")
        cls.normal_user.save()

        cls.reset_data = {
            "password1": "password",
            "password2": "password"
        }

        cls.wrong_data = {
            "password1": "password",
            "password2": "password1"
        }

        cls.request_data = {
            "email": "testuser@tests.com"
        }

        cls.BASE_URL = "http://127.0.0.1:8000"

    def test_request_reset(self):
        test_cases = [
            ({"email": "nelskon@"}, status.HTTP_400_BAD_REQUEST),
            ({"email": "nelie@gmail.com"}, status.HTTP_400_BAD_REQUEST),
            (self.request_data, status.HTTP_200_OK)
        ]

        for data, expected in test_cases:
            with self.subTest(data=data, expected=expected):
                response = self.client.patch(
                    reverse(
                        "request_password_reset"
                    ),
                    data,
                    content_type="application/json"
                )

                print(response.json())

                self.assertEqual(response.status_code, expected)

                if response.status_code == status.HTTP_200_OK:
                    self.token = response.json()["token"]

    def test_reset_password(self):
        self.test_request_reset()

        guid = self.normal_user.guid
        wrong_token = self.normal_user.guid
        test_cases = [
            (self.token, guid, self.wrong_data, status.HTTP_400_BAD_REQUEST),
            (wrong_token, guid, self.reset_data, status.HTTP_400_BAD_REQUEST),
            (self.token, "hah", self.reset_data, status.HTTP_400_BAD_REQUEST),
            (self.token, guid, self.reset_data, status.HTTP_200_OK)
        ]

        for token, guid, data, expected in test_cases:
            with self.subTest(
                token=token,
                guid=guid,
                data=data,
                expected=expected
            ):
                url = f"{self.BASE_URL}/reset_password/{guid}/{token}"

                response = self.client.patch(
                    url,
                    data,
                    content_type="application/json"
                )

                print(response.json())

                self.assertEqual(response.status_code, expected)

                if expected == status.HTTP_200_OK:
                    authenticated_user = raw_authenticate(
                        "testuser",
                        self.reset_data["password1"]
                    )

                    self.assertTrue(authenticated_user is not None)

                    user_model = "<class 'somaafrica.persons.models.User'>"
                    auth_user_model = str(type(authenticated_user))

                    self.assertTrue(auth_user_model == user_model)
                    self.assertTrue(authenticated_user.username == "testuser")
