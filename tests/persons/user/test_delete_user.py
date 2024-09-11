from django.test import TestCase
from django.urls import reverse, exceptions

from model_bakery import baker


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

    def test_delete_own_user(self):
        response = self.client.delete(
            reverse(
                "user-detail",
                kwargs={"pk": self.normal_user.guid}
            ),
            **self.login_headers
        )

        self.assertEqual(response.status_code, 204)

    def test_delete_other_user_as_superuser(self):
        response = self.client.delete(
            reverse(
                "user-detail",
                kwargs={"pk": self.normal_user.guid}
            ),
            **self.super_login_headers
        )

        self.assertEqual(response.status_code, 204)

    def test_delete_other_user_with_normaluser_token(self):

        response = self.client.delete(
            reverse(
                "user-detail",
                kwargs={"pk": self.super_user.guid}
            ),
            **self.login_headers
        )
        print(response.json())

        self.assertContains(response, "No User matches", status_code=404)

    def test_delete_with_no_token(self):
        response = self.client.delete(
            reverse(
                "user-detail",
                kwargs={"pk": self.normal_user.guid}
            ),
        )
        print(response.json())

        self.assertEqual(response.status_code, 401)
        self.assertTrue(
            "credentials were not provided" in response.json()["detail"]
        )

    def test_delete_with_wrong_token(self):
        access_token = "sjsjsjjsskaskskoaoaoakakkakjhdfuyebhdb"
        headers = {
            "HTTP_AUTHORIZATION": f"Bearer {access_token}"
        }

        response = self.client.delete(
            reverse(
                "user-detail",
                kwargs={"pk": self.normal_user.guid}
            ),
            **headers
        )
        print(response.json())

        self.assertEqual(response.status_code, 401)
        self.assertTrue("token not valid" in response.json()["detail"])

    def test_delete_with_pk_missing(self):
        with self.assertRaises(exceptions.NoReverseMatch):
            self.client.delete(
                reverse(
                    "user-detail",
                ),
                **self.login_headers
            )

    def test_invalid_pk(self):
        response = self.client.delete(
            reverse(
                "user-detail",
                kwargs={"pk": "sjjsjksjsjkaakjkjaauwuw"}
            ),
            **self.login_headers
        )
        print(response.json())

        self.assertContains(response, "Not found", status_code=404)
