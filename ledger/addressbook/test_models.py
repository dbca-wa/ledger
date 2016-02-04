from django.test import TestCase
from mixer.backend.django import mixer
from addressbook.models import Address


class AddressTest(TestCase):

    def setUp(self):
        super(AddressTest, self).setUp()
        self.address1 = mixer.blend(Address)

    def test_prop_name(self):
        """Test the Address name property
        """
        a = self.address1
        name = '{} {}'.format(a.first_name, a.last_name)
        self.assertEqual(name, a.name)

    def test_prop_join_fields(self):
        """Test the Address join_fields property
        """
        a = self.address1
        joined = '{}:{}'.format(a.first_name, a.last_name)
        self.assertEqual(
            joined, a.join_fields(['first_name', 'last_name'], ':'))

    def test_clean(self):
        """Test the Address clean method
        """
        a = self.address1
        a.first_name = a.first_name + ' '
        a.save()
        self.assertTrue(a.first_name.endswith(' '))
        a.clean()
        self.assertFalse(a.first_name.endswith(' '))

    def test_str(self):
        """Test the Address __str__ method returns summary property
        """
        a = self.address1
        self.assertEqual(a.summary, str(a))
