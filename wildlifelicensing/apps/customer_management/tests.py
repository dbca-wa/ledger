from django.shortcuts import reverse
from wildlifelicensing.apps.main.tests import helpers as helpers


class LookupViewTest(helpers.BasePermissionViewTestCase):
    view_url = reverse('wl_customer_management:customer_lookup')

    @property
    def permissions(self):
        return {
            'get': {
                'allowed': [self.officer],
                'forbidden': [self.customer, self.assessor],
            },
        }


class CustomerEditDetailsViewTest(helpers.BasePermissionViewTestCase):

    def setUp(self):
        self.view_url = reverse('wl_customer_management:edit_customer_details',
                                args=[self.customer.pk])

    @property
    def permissions(self):
        return {
            'get': {
                'allowed': [self.officer],
                'forbidden': [self.customer, self.assessor],
            },
            'post': {
                'allowed': [self.officer],
                'forbidden': [self.customer, self.assessor],
            }
        }


class CustomerEditProfileViewTest(helpers.BasePermissionViewTestCase):

    def setUp(self):
        self.view_url = reverse('wl_customer_management:edit_customer_profile',
                                args=[self.customer.pk])

    @property
    def permissions(self):
        return {
            'get': {
                'allowed': [self.officer],
                'forbidden': [self.customer, self.assessor],
            },
            'post': {
                'allowed': [self.officer],
                'forbidden': [self.customer, self.assessor],
            }
        }


class CustomerApplicationViewTest(helpers.BasePermissionViewTestCase):

    def setUp(self):
        self.view_url = reverse('wl_customer_management:data_applications',
                                args=[self.customer.pk])

    @property
    def permissions(self):
        return {
            'get': {
                'allowed': [self.officer],
                'forbidden': [self.customer, self.assessor],
            },
            'post': {
                'allowed': [self.officer],
                'forbidden': [self.customer, self.assessor],
            }
        }


class CustomerLicenceViewTest(helpers.BasePermissionViewTestCase):

    def setUp(self):
        self.view_url = reverse('wl_customer_management:data_licences',
                                args=[self.customer.pk])

    @property
    def permissions(self):
        return {
            'get': {
                'allowed': [self.officer],
                'forbidden': [self.customer, self.assessor],
            },
            'post': {
                'allowed': [self.officer],
                'forbidden': [self.customer, self.assessor],
            }
        }


class CustomerReturnViewTest(helpers.BasePermissionViewTestCase):

    def setUp(self):
        self.view_url = reverse('wl_customer_management:data_returns',
                                args=[self.customer.pk])

    @property
    def permissions(self):
        return {
            'get': {
                'allowed': [self.officer],
                'forbidden': [self.customer, self.assessor],
            },
            'post': {
                'allowed': [self.officer],
                'forbidden': [self.customer, self.assessor],
            }
        }