from django.test import TestCase
from mixer.backend.django import mixer
from rollcall.models import EmailUser


class EmailUserTest(TestCase):

    def setUp(self):
        super(EmailUserTest, self).setUp()
        self.user = mixer.blend(EmailUser)

    def test_str(self):
        """Test the EmailUser __str__ method returns email
        """
        self.assertEqual(self.user.email, str(self.user))

    def test_create_user_no_email(self):
        """
        """
        self.assertRaises(ValueError, EmailUser.objects.create_user)

    def test_create_user(self):
        """Test the EmailUser create_user method
        """
        u = EmailUser.objects.create_user('test@email.com')
        self.assertTrue(isinstance(u, EmailUser))

    def test_create_superuser(self):
        """Test the EmailUser create_superuser method
        """
        u = EmailUser.objects.create_superuser('superuser@email.com', '')
        self.assertTrue(isinstance(u, EmailUser))

    def test_get_full_name(self):
        """Test the EmailUser get_full_name method
        """
        n = self.user.get_full_name()
        self.assertEqual(n, '{} {}'.format(self.user.first_name, self.user.last_name))

    def test_short_name(self):
        """Test short_name returns email or first_name
        """
        self.assertEqual(self.user.get_short_name(), self.user.first_name)
        self.user.first_name = ''
        self.user.save()
        self.assertEqual(self.user.get_short_name(), self.user.email)
