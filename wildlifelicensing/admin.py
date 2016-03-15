from django.contrib.admin import AdminSite


class WildlifeLicensingAdminSite(AdminSite):
    site_header = 'Wildlife Licensing Administration'
    site_title = 'Wildlife Licensing'

admin_site = WildlifeLicensingAdminSite(name='wildlifelicensingadmin')
