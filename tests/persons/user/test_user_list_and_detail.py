from django.test import TestCase

from model_bakery import baker


class CrudTest(TestCase):
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
        self.logins = {
            "username": "testuser@tests.com",
            "password": "testuser"
        }
        self.super_logins = {
            "username": "2user",
            "password": "2user"
        }

        self.tokens = self.client.post(
            '/token',
            data=self.logins,
            content_type='application/json'
        )
        self.super_tokens = self.client.post(
            '/token',
            data=self.super_logins,
            content_type='application/json'
        )
        self.access_token = self.tokens.json()["access"]
        self.super_access_token = self.super_tokens.json()["access"]
        self.login_headers = {
            "HTTP_AUTHORIZATION": f"Bearer {self.access_token}"
        }
        self.super_login_headers = {
            "HTTP_AUTHORIZATION": f"Bearer {self.super_access_token}"
        }

    def test_list_as_normal_user(self):
        response = self.client.get('/persons/user', **self.login_headers)
        print(response.json())

        self.assertContains(
            response=response,
            text="testuser",
            status_code=200
        )

    def test_list_as_super_user(self):
        response = self.client.get(
            '/persons/user',
            **self.super_login_headers
        )
        print(response.json())

        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.json()) > 1)

    def test_list_super_user_detail_using_normal_user(self):
        response = self.client.get(
            f"/persons/user/{self.super_user.guid}",
            **self.login_headers
        )
        print(response.json())

        self.assertContains(
            response=response,
            text="No User matches",
            status_code=404
        )

    def test_list_normal_user_detail_using_super_user(self):
        response = self.client.get(
            f"/persons/user/{self.normal_user.guid}",
            **self.super_login_headers
        )
        print(response.json())

        self.assertContains(
            response=response,
            text=self.normal_user.guid,
            status_code=200
        )

    def test_with_no_token(self):
        response = self.client.get(
            "/persons/user"
        )
        print(response.json())

        self.assertContains(
            response=response,
            text="credentials were not provided",
            status_code=401
        )

    def test_with_wrong_token(self):
        access_token = "sjsjsjjsskaskskoaoaoakakkakjhdfuyebhdb"
        headers = {
            "HTTP_AUTHORIZATION": f"Bearer {access_token}"
        }

        response = self.client.get(
            "/persons/user",
            **headers
        )
        print(response.json())

        self.assertContains(
            response=response,
            text="token not valid",
            status_code=401
        )

    def test_with_ordering(self):
        params = {
            "ordering": "username"
        }

        response = self.client.get(
            "/persons/user",
            data=params,
            **self.super_login_headers
        )
        print(response.json())

        self.assertContains(response, "2user", status_code=200)

    def test_with_reverse_ordering(self):
        params = {
            "ordering": "-username"
        }

        response = self.client.get(
            "/persons/user",
            data=params,
            **self.super_login_headers
        )
        print(response.json())

        self.assertContains(response, "testuser", status_code=200)

    def test_with_search_username(self):
        params = {
            "username": "testuser"
        }

        response = self.client.get(
            "/persons/user",
            data=params,
            **self.super_login_headers
        )
        print(response.json())

        self.assertContains(response, "testuser", status_code=200)

    def test_with_search_email(self):
        params = {
            "email": "testuser@tests.com"
        }

        response = self.client.get(
            "/persons/user",
            data=params,
            **self.super_login_headers
        )
        print(response.json())

        self.assertContains(response, "testuser@tests.com", status_code=200)

    def test_with_search_id(self):
        params = {
            "guid": self.normal_user.guid
        }

        response = self.client.get(
            "/persons/user",
            data=params,
            **self.super_login_headers
        )
        print(response.json())

        self.assertContains(response, self.normal_user.guid, status_code=200)

    def test_with_search_invalid_uuid(self):
        params = {
            "guid": "2"
        }

        response = self.client.get(
            "/persons/user",
            data=params,
            **self.super_login_headers
        )
        print(response.json())

        self.assertContains(response, "Enter a valid UUID", status_code=400)

    def test_with_search_id_not_found(self):
        params = {
            "guid": "a43c0664-1ab0-495e-8a0e-75ecb2c09f99"
        }

        response = self.client.get(
            "/persons/user",
            data=params,
            **self.super_login_headers
        )
        print(response.json())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 0)

    def test_with_multiple_filters(self):
        params = {
            "username": "testuser",
            "email": "testuser@tests.com",
            "guid": str(self.normal_user.guid)
        }

        response = self.client.get(
            "/persons/user",
            data=params,
            **self.super_login_headers
        )
        print(response.json())

        self.assertContains(response, "testuser", status_code=200)

    def test_with_wildcard_search(self):
        params = {
            "search": "testuser@tes",
        }

        response = self.client.get(
            "/persons/user",
            data=params,
            **self.super_login_headers
        )
        print(response.json())

        self.assertContains(response, "testuser", status_code=200)

    def test_with_wildcard_search_not_found(self):
        params = {
            "search": "testuser1@tes1",
        }

        response = self.client.get(
            "/persons/user",
            data=params,
            **self.super_login_headers
        )
        print(response.json())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 0)

    def test_with_wildcard_search_not_own_not_superuser(self):
        params = {
            "search": "2user",
        }

        response = self.client.get(
            "/persons/user",
            data=params,
            **self.login_headers
        )
        print(response.json())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 0)
