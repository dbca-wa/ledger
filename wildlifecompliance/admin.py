from django.contrib.admin import AdminSite


class WildlifeComplianceAdminSite(AdminSite):
    site_header = 'WildlifeCompliance Administration'
    site_title = 'WildlifeCompliance Licensing'

wildlifecompliance_admin_site = WildlifeComplianceAdminSite(name='wildlifecomplianceadmin')
