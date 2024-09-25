from django.test import TestCase
from django.urls import reverse
from model_bakery import baker

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

        cls.super_user = baker.make(
            'persons.User',
            make_m2m=True,
            username="2user",
            is_staff=True,
            is_superuser=True
        )
        cls.super_user.set_password("2user")
        cls.super_user.save()

        cls.data = {
            "password1": "password",
            "password2": "password"
        }

    def setUp(self):
        logins = {
            "username": "testuser@tests.com",
            "password": "testuser"
        }
        super_logins = {
            "username": "2user",
            "password": "2user"
        }

        tokens = self.client.post(
            '/token',
            data=logins,
            content_type='application/json'
        )
        super_tokens = self.client.post(
            '/token',
            data=super_logins,
            content_type='application/json'
        )
        access_token = tokens.json()["access"]
        super_access_token = super_tokens.json()["access"]
        self.login_headers = {
            "HTTP_AUTHORIZATION": f"Bearer {access_token}"
        }
        self.super_login_headers = {
            "HTTP_AUTHORIZATION": f"Bearer {super_access_token}"
        }

    def test_change_own_password(self):
        response = self.client.patch(
            reverse(
                "user-change-password",
                kwargs={"pk": self.normal_user.guid}
            ),
            self.data,
            content_type="application/json",
            **self.login_headers
        )
        print(response.json())

        self.assertContains(response, "testuser", status_code=200)

        authenticated_user = raw_authenticate(
            "testuser",
            self.data["password1"]
        )

        self.assertTrue(authenticated_user is not None)

        user_model = "<class 'somaafrica.persons.models.User'>"
        self.assertTrue(str(type(authenticated_user)) == user_model)
        self.assertTrue(authenticated_user.username == "testuser")

    def test_change_other_user_password_as_superuser(self):
        response = self.client.patch(
            reverse(
                "user-change-password",
                kwargs={"pk": self.normal_user.guid}
            ),
            self.data,
            content_type="application/json",
            **self.super_login_headers
        )
        print(response.json())

        self.assertContains(response, "testuser", status_code=200)

        authenticated_user = raw_authenticate(
            "testuser",
            self.data["password1"]
        )

        self.assertTrue(authenticated_user is not None)

        user_model = "<class 'somaafrica.persons.models.User'>"
        self.assertTrue(str(type(authenticated_user)) == user_model)
        self.assertTrue(authenticated_user.username == "testuser")

    def test_other_user_details_with_normaluser_token(self):
        response = self.client.patch(
            reverse(
                "user-change-password",
                kwargs={"pk": self.super_user.guid}
            ),
            self.data,
            content_type="application/json",
            **self.login_headers
        )
        print(response.json())

        self.assertEqual(response.status_code, 400)
        self.assertTrue("No User matches" in response.json()["detail"])

    def test_with_no_token(self):
        response = self.client.patch(
            reverse(
                "user-change-password",
                kwargs={"pk": self.normal_user.guid}
            ),
            self.data
        )
        print(response.json())

        self.assertEqual(response.status_code, 401)
        self.assertTrue(
            "credentials were not provided" in response.json()["detail"]
        )

    def test_with_wrong_token(self):
        access_token = "sjsjsjjsskaskskoaoaoakakkakjhdfuyebhdb"
        headers = {
            "HTTP_AUTHORIZATION": f"Bearer {access_token}"
        }

        response = self.client.patch(
            reverse(
                "user-change-password",
                kwargs={"pk": self.normal_user.guid}
            ),
            self.data,
            content_type="application/json",
            **headers
        )
        print(response.json())

        self.assertEqual(response.status_code, 401)
        self.assertTrue("token not valid" in response.json()["detail"])

    def test_password_missing(self):
        response = self.client.patch(
            reverse(
                "user-change-password",
                kwargs={"pk": self.normal_user.guid}
            ),
            content_type="application/json",
            **self.login_headers
        )
        print(response.json())

        self.assertContains(response, "field is required", status_code=400)

    def test_password_mismatch(self):
        data = {
            "password1": "password",
            "password2": "pass"
        }

        response = self.client.patch(
            reverse(
                "user-change-password",
                kwargs={"pk": self.normal_user.guid}
            ),
            data,
            content_type="application/json",
            **self.login_headers
        )
        print(response.json())

        self.assertContains(response, "Password mismatch", status_code=400)
