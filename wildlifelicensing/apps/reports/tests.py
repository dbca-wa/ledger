from django.core.urlresolvers import reverse

from wildlifelicensing.apps.main.tests import helpers


class ReportsViewTestCase(helpers.BasePermissionViewTestCase):
    view_url = reverse('wl_reports:reports')

    @property
    def permissions(self):
        return {
            'get': {
                'allowed': [self.officer],
                'forbidden': [self.customer, self.assessor],
            },
        }

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
