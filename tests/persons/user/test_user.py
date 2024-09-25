from django.urls import reverse
from model_bakery import baker

from somaafrica.persons.models import User

from .crud import CRUD


class UserTests(CRUD):
    model = User
    base_url_name = 'user'

    def setUp(self):
        self.data = baker.prepare(self.model).__dict__
        self.data.pop('_state', None)
        self.data.pop('guid', None)

        self.persistent_data = baker.make(
            self.model,
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

    def test_method_not_found(self):
        response = self.client.options(
            reverse(
                "user-detail",
                kwargs={"pk": self.persistent_data[4].guid}
            ),
            data=self.data,
            content_type="application/json",
            **self.super_login_headers
        )

        print(response.json())
        self.assertContains(response, "not allowed", status_code=405)

    def test_user_str_(self):
        guid = self.persistent_data[0].guid
        username = self.persistent_data[0].username
        email = self.persistent_data[0].email
        user = f"{guid} - {username} - {email}"

        self.assertEqual(
            str(self.persistent_data[0]),
            user
        )

    def test_user_has_perms(self):
        with self.assertRaises(ValueError):
            self.persistent_data[0].has_perms("add_user")

    def test_create_super_user(self):
        data = {
            "username": "testing_super",
            "password": "testing_super"
        }
        response = User.objects.create_superuser(**data)

        print(response)
        self.assertEqual(response.username, "testing_super")
