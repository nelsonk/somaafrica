from django.urls import reverse
from rest_framework import status
from model_bakery import baker

from .setupdata import SetUpData


class PermissionTests(SetUpData):
    model = "auth.Permission"

    def setUp(self):
        self.data = baker.prepare(self.model).__dict__
        self.data.pop('_state', None)
        self.data.pop('id', None)

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

        real_pk = self.persistent_data[4].id
        fake_pk = "hjssjjsksnskjkbbkskjshkjkjsjhksjk"
        self.test_cases = [
            (self.login_headers, real_pk, status.HTTP_200_OK),
            (self.super_login_headers, real_pk, status.HTTP_200_OK),
            (self.super_login_headers, fake_pk, status.HTTP_404_NOT_FOUND)
        ]

    def test_get_permission(self):
        for headers, pk, expected in self.test_cases:
            with self.subTest(headers=headers, pk=pk):
                response = self.client.get(
                    reverse("permission-detail", kwargs={"pk": pk}),
                    **headers
                )

                print(response.json())
                self.assertEqual(response.status_code, expected)

    def test_post_permissions(self):
        response = self.client.post(
            reverse("permission-list"),
            data=self.data,
            content_type="application/json()",
            **self.super_login_headers
        )

        print(response.json())
        self.assertContains(
            response,
            'not allowed',
            status_code=405
        )

    def test_list_permissions(self):
        response = self.client.get(
            reverse("permission-list"),
            **self.login_headers
        )

        print(response.json())
        self.assertContains(
            response,
            self.persistent_data[4].id,
            status_code=200
        )
