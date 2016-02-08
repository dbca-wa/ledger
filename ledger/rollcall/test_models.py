from django.test import TestCase
from mixer.backend.django import mixer
from rollcall.models import EmailUser


class EmailUserTest(TestCase):

    def setUp(self):
        super(EmailUserTest, self).setUp()
        self.user = mixer.blend(EmailUser)

    def test_save(self):
        """Test the EmailUser save() method doesn't except due to overrides
        """
        self.user.save()

    def test_str(self):
        """Test the EmailUser __str__ method returns email
        """
        self.assertEqual(self.user.email, str(self.user))
