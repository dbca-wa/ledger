from django.test import TestCase


class ReportsTestCase(TestCase):
    fixtures = ['licences.json']

    def setUp(self):
        pass

    def test_report_menu(self):
        """Testing that a user can access the main report generation menu screen"""
        pass

    def test_applications_report(self):
        """Testing that a user can create an applications report"""
        pass

    def test_licences_report(self):
        """Testing that a user can create a licences report"""
        pass

    def test_returns_report(self):
        """Testing that a user can create an returns report"""
        pass
