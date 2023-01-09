from django.test import TestCase
from users.models import User


class TestAppModels(TestCase):
    def setUp(self):
        self.user = User(username="testuser")
        self.user.set_password("testpassword")
        self.user.save()

    def test_user_created(self):
        self.assertIsNotNone(self.user)
