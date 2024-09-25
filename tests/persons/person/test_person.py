from django.urls import reverse

from rest_framework import status
from model_bakery import baker

from somaafrica.persons.models import Person
from tests.persons.user.crud import CRUD


class PersonTests(CRUD):
    model = Person
    base_url_name = 'person'

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

        self.phone_data = {
            "number": "+256779341293",
            "created_by": self.normal_user.guid,
            "updated_by": self.normal_user.guid
        }

        self.address_data = {
            "address": "Kampala, Uganda",
            "created_by": self.normal_user.guid,
            "updated_by": self.normal_user.guid
        }

        real_pk = self.persistent_data[4].guid
        fake_pk = "hjssjjsksnskjkbbkskjshkjkjsjhksjk"
        self.test_cases = [
            (self.login_headers, real_pk, status.HTTP_403_FORBIDDEN),
            (self.super_login_headers, real_pk, status.HTTP_200_OK),
            (self.super_login_headers, fake_pk, status.HTTP_400_BAD_REQUEST)
        ]

    def test_add_user(self):
        data = {"user_guid": self.normal_user.guid}

        for headers, pk, expected in self.test_cases:
            with self.subTest(headers=headers, pk=pk):
                response = self.client.patch(
                    reverse(
                        "person-add-user",
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
                        "person-remove-user",
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

    def test_add_fake_user(self):
        data = {"user_guid": self.persistent_data[0].guid}

        response = self.client.patch(
            reverse(
                "person-add-user",
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

    def test_add_phone(self):
        for headers, pk, expected in self.test_cases:
            with self.subTest(headers=headers, pk=pk):
                response = self.client.patch(
                    reverse(
                        "person-add-phone",
                        kwargs={"pk": pk}
                    ),
                    data=self.phone_data,
                    content_type="application/json",
                    **headers
                )

                print(response.json())
                self.assertEqual(response.status_code, expected)

                if expected == status.HTTP_200_OK:
                    self.assertContains(
                        response,
                        self.phone_data["number"],
                        status_code=200
                    )

    def test_invalid_phone_number(self):
        testcases = [
            ("770127391", "is not a valid phone number format"),
            ("+256727123", "not a valid international number")
        ]

        for phone, expected in testcases:
            phone_data = {
                "number": phone,
                "created_by": self.normal_user.guid,
                "updated_by": self.normal_user.guid
            }

            with self.subTest(phone_data=phone_data):
                response = self.client.patch(
                    reverse(
                        "person-add-phone",
                        kwargs={"pk": self.persistent_data[4].guid}
                    ),
                    data=phone_data,
                    content_type="application/json",
                    **self.super_login_headers
                )

                print(response.json())

                self.assertContains(
                    response,
                    expected,
                    status_code=status.HTTP_400_BAD_REQUEST
                )

    def test_remove_phone(self):
        self.test_add_phone()

        for headers, pk, expected in self.test_cases:
            with self.subTest(headers=headers, pk=pk):
                response = self.client.patch(
                    reverse(
                        "person-remove-phone",
                        kwargs={"pk": pk}
                    ),
                    data=self.phone_data,
                    content_type="application/json",
                    **headers
                )

                print(response.json())
                self.assertEqual(response.status_code, expected)

                if expected == status.HTTP_200_OK:
                    self.assertNotIn(
                        self.phone_data["number"],
                        response.json()
                    )

    def test_add_address(self):
        for headers, pk, expected in self.test_cases:
            with self.subTest(headers=headers, pk=pk):
                response = self.client.patch(
                    reverse(
                        "person-add-address",
                        kwargs={"pk": pk}
                    ),
                    data=self.address_data,
                    content_type="application/json",
                    **headers
                )

                print(response.json())
                self.assertEqual(response.status_code, expected)

                if expected == status.HTTP_200_OK:
                    self.assertContains(
                        response,
                        self.address_data["address"],
                        status_code=200
                    )

    def test_remove_address(self):
        self.test_add_address()

        for headers, pk, expected in self.test_cases:
            with self.subTest(headers=headers, pk=pk):
                response = self.client.patch(
                    reverse(
                        "person-remove-address",
                        kwargs={"pk": pk}
                    ),
                    data=self.address_data,
                    content_type="application/json",
                    **headers
                )

                print(response.json())
                self.assertEqual(response.status_code, expected)

                if expected == status.HTTP_200_OK:
                    self.assertNotIn(
                        self.address_data["address"],
                        response.json()
                    )

    def test_remove_fake_phone(self):
        data = {"number": "7892928998"}

        response = self.client.patch(
            reverse(
                "person-remove-phone",
                kwargs={"pk": self.persistent_data[4].guid}
            ),
            data=data,
            content_type="application/json",
            **self.super_login_headers
        )

        print(response.json())
        self.assertContains(response, "does not exist", status_code=400)

    def test_remove_fake_address(self):
        data = {
            "address": "7892928998",
            "created_by": self.normal_user.guid,
            "updated_by": self.normal_user.guid
            }

        response = self.client.patch(
            reverse(
                "person-remove-address",
                kwargs={"pk": self.persistent_data[4].guid}
            ),
            data=data,
            content_type="application/json",
            **self.super_login_headers
        )

        print(response.json())
        self.assertContains(response, "does not exist", status_code=400)

    def test_add_phone_address_exception(self):
        with self.assertRaises(TypeError):
            self.persistent_data[0].add_phone("898918919")

        with self.assertRaises(TypeError):
            self.persistent_data[0].add_address("898918919")
