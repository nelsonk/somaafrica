import abc

from django.test import TestCase
from django.urls import reverse
from model_bakery import baker


class CRUD(TestCase, metaclass=abc.ABCMeta):
    model = None
    base_url_name = ''

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

    @abc.abstractmethod
    def setUp(self):
        """This method should be defined in the child class"""
        if self.model is None:
            raise NotImplementedError(
                "Subclasses must define 'model' and related attributes."
            )

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
                kwargs={"pk": self.persistent_data[0].guid}
            ),
            **self.super_login_headers
        )
        print(response)

        self.assertContains(
            response,
            self.persistent_data[0].guid,
            status_code=200
        )

    def test_post_with_super_user(self):
        response = self.client.post(
            reverse(f"{self.base_url_name}-list"),
            data=self.data,
            content_type='application/json',
            **self.super_login_headers
        )
        print(response.json())

        self.assertEqual(response.status_code, 201)
        # self.assertTrue(
        # self.__class__.model.objects.filter(id=self.data['id']).exists()
        # )

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
                kwargs={"pk": self.persistent_data[0].guid}
            ),
            data=self.data,
            content_type='application/json',
            **self.super_login_headers
        )
        print(response.json())

        self.assertEqual(response.status_code, 200)

    def test_put_un_authenticated(self):
        response = self.client.put(
            reverse(
                f"{self.base_url_name}-detail",
                kwargs={"pk": self.persistent_data[0].guid}
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
                kwargs={"pk": self.persistent_data[0].guid}
            ),
            **self.super_login_headers
        )
        print(response)

        our_id = self.persistent_data[0].guid
        self.assertFalse(
            self.__class__.model.objects.filter(guid=our_id).exists()
        )

    def test_delete_un_authenticated(self):
        response = self.client.delete(
            reverse(
                f"{self.base_url_name}-detail",
                kwargs={"pk": self.persistent_data[0].guid}
            )
        )
        print(response)

        self.assertContains(
            response,
            "credentials were not provided",
            status_code=401
        )
