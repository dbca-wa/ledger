from django.contrib.admin import AdminSite


class WildlifeLicensingAdminSite(AdminSite):
    site_header = 'Wildlife Licensing Administration'
    site_title = 'Wildlife Licensing'

wildlife_licensing_admin_site = WildlifeLicensingAdminSite(name='wildlifelicensingadmin')
