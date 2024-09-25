from django.urls import reverse
from model_bakery import baker
from rest_framework import status

from somaafrica.persons.models import Group

from .crud import CRUD


class GroupTests(CRUD):
    model = Group
    base_url_name = 'group'

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

        real_pk = self.persistent_data[4].guid
        fake_pk = "hjssjjsksnskjkbbkskjshkjkjsjhksjk"
        self.test_cases = [
            (self.login_headers, real_pk, status.HTTP_403_FORBIDDEN),
            (self.super_login_headers, real_pk, status.HTTP_200_OK),
            (self.super_login_headers, fake_pk, status.HTTP_400_BAD_REQUEST)
        ]

    def test_add_permissions(self):
        data = {"permissions": ["add_group", "change_group"]}

        for headers, pk, expected in self.test_cases:
            with self.subTest(headers=headers, pk=pk):
                response = self.client.patch(
                    reverse(
                        "group-add-permissions",
                        kwargs={"pk": pk}
                    ),
                    data=data,
                    content_type="application/json",
                    **headers
                )

                print(response.json())
                self.assertEqual(response.status_code, expected)

                if expected == status.HTTP_200_OK:
                    self.assertContains(response, "add_group", status_code=200)
                    self.assertContains(
                        response,
                        "change_group",
                        status_code=200
                    )

    def test_add_remove_fake_permissions(self):
        data = {"permissions": ["fake_test"]}

        testcases = [
            ("group-add-permissions"),
            ("group-remove-permissions")
        ]

        for target in testcases:
            with self.subTest(target=target):
                response = self.client.patch(
                    reverse(
                        target,
                        kwargs={"pk": self.persistent_data[4].guid}
                    ),
                    data=data,
                    content_type="application/json",
                    **self.super_login_headers
                )

                print(response.json())
                self.assertContains(
                    response,
                    "No valid permissions found",
                    status_code=400
                )

    def test_remove_permissions(self):
        self.test_add_permissions()

        data = {"permissions": ["change_group"]}

        for headers, pk, expected in self.test_cases:
            with self.subTest(headers=headers, pk=pk):
                response = self.client.patch(
                    reverse(
                        "group-remove-permissions",
                        kwargs={"pk": pk}
                    ),
                    data=data,
                    content_type="application/json",
                    **headers
                )

                print(response.json())
                self.assertEqual(response.status_code, expected)

                if expected == status.HTTP_200_OK:
                    self.assertContains(response, "add_group", status_code=200)
                    self.assertNotIn("change_group", response.json())

    def test_add_user(self):
        data = {"user_guid": self.normal_user.guid}

        for headers, pk, expected in self.test_cases:
            with self.subTest(headers=headers, pk=pk):
                response = self.client.patch(
                    reverse(
                        "group-add-user",
                        kwargs={"pk": pk}
                    ),
                    data=data,
                    content_type="application/json",
                    **headers
                )

                print(response.json())
                self.assertEqual(response.status_code, expected)

                if expected == status.HTTP_200_OK:
                    self.assertContains(
                        response,
                        self.normal_user.guid,
                        status_code=200
                    )

    def test_remove_user(self):
        self.test_add_user()

        data = {"user_guid": self.normal_user.guid}

        for headers, pk, expected in self.test_cases:
            with self.subTest(headers=headers, pk=pk):
                response = self.client.patch(
                    reverse(
                        "group-remove-user",
                        kwargs={"pk": pk}
                    ),
                    data=data,
                    content_type="application/json",
                    **headers
                )

                print(response.json())
                self.assertEqual(response.status_code, expected)

                if expected == status.HTTP_200_OK:
                    self.assertNotIn(self.normal_user.guid, response.json())

    def test_add_remove_fake_user(self):
        data = {"user_guid": self.persistent_data[0].guid}

        testcases = [
            ("group-add-user"),
            ("group-remove-user")
        ]

        for target in testcases:
            with self.subTest(target=target):
                response = self.client.patch(
                    reverse(
                        target,
                        kwargs={"pk": self.persistent_data[4].guid}
                    ),
                    data=data,
                    content_type="application/json",
                    **self.super_login_headers
                )

                print(response.json())
                self.assertContains(
                    response,
                    "does not exist",
                    status_code=400
                )

    def test_group_natural_key_and_str_(self):
        self.assertEqual(
            str(self.persistent_data[0]),
            self.persistent_data[0].name
        )

        self.assertEqual(
            str(self.persistent_data[0].natural_key()[0]),
            self.persistent_data[0].name
        )

        name = self.persistent_data[0].name
        self.assertEqual(
            Group.objects.get_by_natural_key(name),
            self.persistent_data[0]
        )
