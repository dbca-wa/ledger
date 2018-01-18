from django.contrib.admin import AdminSite


class DisturbanceAdminSite(AdminSite):
    site_header = 'Disturbance Administration'
    site_title = 'Disturbance Licensing'

disturbance_admin_site = DisturbanceAdminSite(name='disturbanceadmin')
