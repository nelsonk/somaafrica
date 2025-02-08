from django.test import TestCase
from django.urls import reverse

from rest_framework import status


class TestAPI(TestCase):

    def test_api_health(self):
        response = self.client.get(reverse("health_check"))

        self.assertContains(
            response,
            "healthy",
            status_code=status.HTTP_200_OK
        )
