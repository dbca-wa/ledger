from django.shortcuts import reverse
from wildlifelicensing.apps.main.tests import helpers as helpers


class RoutingViewTest(helpers.BasePermissionViewTestCase):
    view_url = reverse('home')

    @property
    def permissions(self):
        return {
            'get': {
                'allowed': self.all_users,
                'forbidden': [],
                'kwargs': {
                    'follow': True
                }
            },
        }


class TreeViewTest(helpers.BasePermissionViewTestCase):
    view_url = reverse('wl_dashboard:tree_officer')

    @property
    def permissions(self):
        return {
            'get': {
                'allowed': [self.officer],
                'forbidden': [self.assessor, self.customer],
            },
        }


class TableCustomerViewTest(helpers.BasePermissionViewTestCase):
    view_url = reverse('wl_dashboard:tables_customer')

    @property
    def permissions(self):
        return {
            'get': {
                'allowed': self.all_users,
                'forbidden': [],
            },
        }


class TableAssessorViewTest(helpers.BasePermissionViewTestCase):
    view_url = reverse('wl_dashboard:tables_assessor')

    @property
    def permissions(self):
        return {
            'get': {
                'allowed': [self.assessor],
                'forbidden': [self.officer, self.customer],
            },
        }


class TableApplicationOfficerViewTest(helpers.BasePermissionViewTestCase):
    view_url = reverse('wl_dashboard:tables_applications_officer')

    @property
    def permissions(self):
        return {
            'get': {
                'allowed': [self.officer],
                'forbidden': [self.assessor, self.customer],
            },
        }


class DataTableApplicationOfficerViewTest(helpers.BasePermissionViewTestCase):
    view_url = reverse('wl_dashboard:data_application_officer')

    @property
    def permissions(self):
        return {
            'get': {
                'allowed': [self.officer],
                'forbidden': [self.assessor, self.customer],
            },
            'post': {
                'allowed': [self.officer],
                'forbidden': [self.assessor, self.customer],
            },
        }


class TableApplicationOfficerOnBehalfViewTest(helpers.BasePermissionViewTestCase):
    view_url = reverse('wl_dashboard:tables_officer_onbehalf')

    @property
    def permissions(self):
        return {
            'get': {
                'allowed': [self.officer],
                'forbidden': [self.assessor, self.customer],
            },
        }


class DataTableApplicationOfficerOnBehalfViewTest(helpers.BasePermissionViewTestCase):
    view_url = reverse('wl_dashboard:data_application_officer_onbehalf')

    @property
    def permissions(self):
        return {
            'get': {
                'allowed': [self.officer],
                'forbidden': [self.assessor, self.customer],
            },
            'post': {
                'allowed': [self.officer],
                'forbidden': [self.assessor, self.customer],
            },
        }


class DataTableApplicationCustomerViewTest(helpers.BasePermissionViewTestCase):
    view_url = reverse('wl_dashboard:data_application_customer')

    @property
    def permissions(self):
        return {
            'get': {
                'allowed': self.all_users,
                'forbidden': [],
            },
            'post': {
                'allowed': self.all_users,
                'forbidden': [],
            },
        }


class DataTableApplicationAssessorViewTest(helpers.BasePermissionViewTestCase):
    view_url = reverse('wl_dashboard:data_application_assessor')

    @property
    def permissions(self):
        return {
            'get': {
                'allowed': [self.officer, self.assessor],
                'forbidden': [self.customer],
            },
            'post': {
                'allowed': [self.officer, self.assessor],
                'forbidden': [self.customer],
            },
        }


class TableLicenceOfficerViewTest(helpers.BasePermissionViewTestCase):
    view_url = reverse('wl_dashboard:tables_licences_officer')

    @property
    def permissions(self):
        return {
            'get': {
                'allowed': [self.officer],
                'forbidden': [self.assessor, self.customer],
            },
        }


class DataTableLicenceOfficerViewTest(helpers.BasePermissionViewTestCase):
    view_url = reverse('wl_dashboard:data_licences_officer')

    @property
    def permissions(self):
        return {
            'get': {
                'allowed': [self.officer],
                'forbidden': [self.assessor, self.customer],
            },
            'post': {
                'allowed': [self.officer],
                'forbidden': [self.assessor, self.customer],
            },
        }


class DataTableLicenceCustomerViewTest(helpers.BasePermissionViewTestCase):
    view_url = reverse('wl_dashboard:data_licences_customer')

    @property
    def permissions(self):
        return {
            'get': {
                'allowed': self.all_users,
                'forbidden': [],
            },
            'post': {
                'allowed': self.all_users,
                'forbidden': [],
            },
        }


class BulkLicenceRenewalCustomerViewTest(helpers.BasePermissionViewTestCase):
    view_url = reverse('wl_dashboard:bulk_licence_renewal_pdf')

    @property
    def permissions(self):
        return {
            'get': {
                'allowed': [self.officer],
                'forbidden': [self.assessor, self.customer],
            },
            'post': {
                'allowed': [self.officer],
                'forbidden': [self.assessor, self.customer],
            },
        }


class TableReturnOfficerViewTest(helpers.BasePermissionViewTestCase):
    view_url = reverse('wl_dashboard:tables_returns_officer')

    @property
    def permissions(self):
        return {
            'get': {
                'allowed': [self.officer],
                'forbidden': [self.assessor, self.customer],
            },
        }


class DataTableReturnOfficerViewTest(helpers.BasePermissionViewTestCase):
    view_url = reverse('wl_dashboard:data_returns_officer')

    @property
    def permissions(self):
        return {
            'get': {
                'allowed': [self.officer],
                'forbidden': [self.assessor, self.customer],
            },
            'post': {
                'allowed': [self.officer],
                'forbidden': [self.assessor, self.customer],
            },
        }


class DataTableReturnOnBehalfViewTest(helpers.BasePermissionViewTestCase):
    view_url = reverse('wl_dashboard:data_returns_officer_onbehalf')

    @property
    def permissions(self):
        return {
            'get': {
                'allowed': [self.officer],
                'forbidden': [self.assessor, self.customer],
            },
            'post': {
                'allowed': [self.officer],
                'forbidden': [self.assessor, self.customer],
            },
        }


class DataTableCustomerCustomerViewTest(helpers.BasePermissionViewTestCase):
    view_url = reverse('wl_dashboard:data_returns_customer')

    @property
    def permissions(self):
        return {
            'get': {
                'allowed': self.all_users,
                'forbidden': [],
            },
            'post': {
                'allowed': self.all_users,
                'forbidden': [],
            },
        }
