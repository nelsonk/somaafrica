import os

from django.test import TestCase

from somaafrica.configs import settings


class Testing(TestCase):
    def test_github_env(self):
        # Set the environment variable
        os.environ['GITHUB_WORKFLOW'] = 'true'

        from importlib import reload
        reload(settings)

        self.assertEqual(settings.DATABASES['default']['USER'], "postgres")

    def test_no_github_env(self):
        # Set the environment variable
        del os.environ['GITHUB_WORKFLOW']

        from importlib import reload
        reload(settings)

        self.assertEqual(settings.DATABASES['default']['USER'], "somaafrica")
