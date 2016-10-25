from django.test import TestCase
from django.core.urlresolvers import reverse


class TestExplorerView(TestCase):
    fixtures = [
        'countries',
        'groups',
        'licences',
        'conditions',
        'default-conditions',
        'returns'
    ]

    def test_authorisation(self):
        """
        Only admin or API users
        :return:
        """


class TestDataView(TestCase):
    pass
