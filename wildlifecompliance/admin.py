from django.contrib.admin import AdminSite


class WildlifeComplianceAdminSite(AdminSite):
    site_header = 'Wildlife Licensing System Administration'
    site_title = 'Wildlife Licensing System'

wildlifecompliance_admin_site = WildlifeComplianceAdminSite(name='wildlifecomplianceadmin')
