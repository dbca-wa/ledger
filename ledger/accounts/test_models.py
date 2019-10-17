from django.test import TestCase
from django_dynamic_fixture import get as get_ddf
from ledger.accounts.models import EmailUser, Address, Country


class EmailUserTest(TestCase):

    def setUp(self):
        super(EmailUserTest, self).setUp()
        self.user = get_ddf(EmailUser, dob='1970-01-01')

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


class AddressTest(TestCase):

    def setUp(self):
        super(AddressTest, self).setUp()
        get_ddf(Country, iso_3166_1_a2='AU')
        self.address1 = get_ddf(Address, country='AU')

    def test_prop_join_fields(self):
        """Test the Address join_fields property
        """
        a = self.address1
        joined = '{}:{}'.format(a.line1, a.postcode)
        self.assertEqual(
            joined, a.join_fields(['line1', 'postcode'], ':'))

    def test_clean(self):
        """Test the Address clean method
        """
        a = self.address1
        a.line1 += ' '
        a.save()
        self.assertTrue(a.line1.endswith(' '))
        a.clean()
        self.assertFalse(a.line1.endswith(' '))

    def test_str(self):
        """Test the Address __str__ method returns summary property
        """
        a = self.address1
        self.assertEqual(a.summary, str(a))

