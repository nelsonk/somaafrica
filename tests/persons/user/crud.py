from django.test import TestCase
from django.urls import reverse

from model_bakery import baker

from somaafrica.persons.models import User


class CRUD(TestCase):
    model = User
    base_url_name = 'user'

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

        cls.logins = {
            "username": "testuser@tests.com",
            "password": "testuser"
        }
        cls.super_logins = {
            "username": "2user",
            "password": "2user"
        }

    def setUp(self):
        print(f"Running setUp in {self.__class__.__name__}, model: {self.__class__.model}")

        self.data = baker.prepare(self.__class__.model).__dict__
        self.data.pop('_state', None)
        self.data.pop('id', None)

        self.persistent_data = baker.make(
            self.__class__.model,
            _quantity=5,
            make_m2m=True
        )

        self.tokens = self.client.post(
            '/token',
            data=self.logins,
            content_type='application/json'
        )
        self.access_token = self.tokens.json()["access"]
        self.login_headers = {
            "HTTP_AUTHORIZATION": f"Bearer {self.access_token}"
        }

        self.super_tokens = self.client.post(
            '/token',
            data=self.super_logins,
            content_type='application/json'
        )
        self.super_access_token = self.super_tokens.json()["access"]
        self.super_login_headers = {
            "HTTP_AUTHORIZATION": f"Bearer {self.super_access_token}"
        }

    def test_get_with_super_user(self):
        response = self.client.get(
            reverse(
                f"{self.base_url_name}-list",
            ),
            **self.super_login_headers
        )
        print(response.json())

        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.json()) > 1)

    def test_get_detail_with_super_user(self):
        response = self.client.get(
            reverse(
                f"{self.base_url_name}-detail",
                kwargs={"pk": self.persistent_data[0].id}
            ),
            **self.super_login_headers
        )
        print(response)

        self.assertContains(response, self.persistent_data[0].id, status_code=200)

    def test_post_with_super_user(self):
        response = self.client.post(
            reverse(f"{self.base_url_name}-list"),
            data=self.data,
            content_type='application/json',
            **self.super_login_headers
        )
        print(response.json())

        self.assertEqual(response.status_code, 201)
        #self.assertTrue(self.__class__.model.objects.filter(id=self.data['id']).exists())

    def test_post_un_authenticated(self):
        response = self.client.post(
            reverse(f"{self.base_url_name}-list"),
            data=self.data,
            content_type='application/json'
        )
        print(response.json())

        self.assertContains(
            response,
            "credentials were not provided",
            status_code=401
        )

    def test_put_with_super_user(self):
        response = self.client.put(
            reverse(
                f"{self.base_url_name}-detail",
                kwargs={"pk": self.persistent_data[0].id}
            ),
            data=self.data,
            content_type='application/json',
            **self.super_login_headers
        )
        print(response.json())

        #self.__class__.model.refresh_from_db(self.__class__.model)
        self.assertEqual(response.status_code, 200)
        #self.assertTrue(self.__class__.model.objects.filter(id=self.data['id']).exists())

    def test_put_un_authenticated(self):
        response = self.client.put(
            reverse(
                f"{self.base_url_name}-detail",
                kwargs={"pk": self.persistent_data[0].id}
            ),
            data=self.data,
            content_type='application/json'
        )
        print(response.json())

        self.assertContains(
            response,
            "credentials were not provided",
            status_code=401
        )

    def test_delete_with_super_user(self):
        response = self.client.delete(
            reverse(
                f"{self.base_url_name}-detail",
                kwargs={"pk": self.persistent_data[0].id}
            ),
            **self.super_login_headers
        )
        print(response)

        our_id = self.persistent_data[0].id
        self.assertFalse(self.__class__.model.objects.filter(id=our_id).exists())

    def test_delete_un_authenticated(self):
        response = self.client.delete(
            reverse(
                f"{self.base_url_name}-detail",
                kwargs={"pk": self.persistent_data[0].id}
            )
        )
        print(response)

        self.assertContains(
            response,
            "credentials were not provided",
            status_code=401
        )
